import torch
import torch.nn as nn
from torch.autograd import Variable
from torchvision.utils import save_image
import torchvision.transforms as transforms
from torch.nn.functional import pad
from torchvision.utils import save_image


class LRLoss(nn.Module):
    def __init__(self):
        super(LRLoss, self).__init__()

    def forward(self, disp_left,disp_right, left, right):
        estRight = self.bilinear_sampler_1d_h(left, disp_right)
        estLeft = self.bilinear_sampler_1d_h(right, -1 * disp_left)
        gray_left = self.getGrayImage(left)
        gray_right = self.getGrayImage(right)
        gray_estLeft = self.getGrayImage(estLeft)
        gray_esttRight = self.getGrayImage(estRight)

        # # 1. Image Reconstruction loss
        SAD_left = torch.mean(torch.abs(left - estLeft))
        SAD_right = torch.mean(torch.abs(right - estRight))

        SSIM_left = 0.5 * self.SSIM1(gray_left,gray_estLeft,3) + 0.5 * self.SSIM1(gray_left,gray_estLeft,5)
        SSIM_right = 0.5 * self.SSIM1(gray_right,gray_esttRight,3) + 0.5 * self.SSIM1(gray_right,gray_esttRight,5)

        alpha = 0.5
        rec_loss_right = alpha * SSIM_right + (1 - alpha) * SAD_right
        rec_loss_left = alpha * SSIM_left + (1 - alpha) * SAD_left
        REC_loss = rec_loss_left + rec_loss_right

        # 2. DISPARITY SMOOTHNESS
        left_disp_smooth = self.LaplacianLayer(disp_left, left)
        right_disp_smooth = self.LaplacianLayer(disp_right, right)
        disp_smooth_loss = left_disp_smooth + right_disp_smooth

        # 3. LR consistency loss
        LtoR = self.bilinear_sampler_1d_h(disp_left, disp_right)
        RtoL = self.bilinear_sampler_1d_h(disp_right, -1 * disp_left)
        lr_left_loss = torch.mean(torch.abs(RtoL - disp_left))
        lr_right_loss = torch.mean(torch.abs(LtoR - disp_right))
        lr_loss = lr_left_loss + lr_right_loss


        if(True):
            save_image(right, 'right.png')
            save_image(left, 'left.png')
            save_image(estRight, 'estRight.png')
            save_image(estLeft, 'estLeft.png')
            save_image(disp_right/torch.max(disp_right), 'disp_right.png')
            save_image(disp_left/torch.max(disp_left), 'disp_left.png')

        return 1 * REC_loss, 0.2 * disp_smooth_loss,  0.5 * lr_loss


#Bilinear sampler in pytorch(https://github.com/alwynmathew/bilinear-sampler-pytorch)
    def bilinear_sampler_1d_h(self,input_images, x_offset, wrap_mode="border", tensor_type='torch.cuda.FloatTensor'):

        num_batch = input_images.size(0)
        num_channels = input_images.size(1)
        height = input_images.size(2)
        width = input_images.size(3)

        edge_size = 0
        if wrap_mode == "border":
            edge_size = 1
            input_images = pad(input_images, (1, 1, 1, 1))
        elif wrap_mode == 'edge':
            edge_size = 0
        else:
            return None

        im_flat = input_images.view(num_channels, -1)

        # Create meshgrid for pixel indicies (PyTorch doesn't have dedicated
        # meshgrid function)
        x = torch.linspace(0, width - 1, width).repeat(height,
                                                    1).type(tensor_type).cuda()
        y = torch.linspace(0, height - 1, height).repeat(width,
                                                        1).transpose(0, 1).type(tensor_type).cuda()
        # Take padding into account
        x = x + edge_size
        y = y + edge_size

        # Flatten and repeat for each image in the batch

        #TO DO! use best one
        x = x.contiguous().view(-1).repeat(1, num_batch)
        y = y.contiguous().view(-1).repeat(1, num_batch)


        # Now we want to sample pixels with indicies shifted by disparity in X direction
        # For that we convert disparity from % to pixels and add to X indicies
        x = x + x_offset.type(tensor_type).contiguous().view(-1)
        # x = x + x_offset.type(tensor_type).contiguous().view(-1) * width
        # Make sure we don't go outside of image
        x = torch.clamp(x, 0.0, width - 1 + 2 * edge_size)
        # Round disparity to sample from integer-valued pixel grid
        y0 = torch.floor(y)
        # In X direction round both down and up to apply linear interpolation
        # between them later
        x0 = torch.floor(x)
        x1 = x0 + 1
        # After rounding up we might go outside the image boundaries again
        x1 = x1.clamp(max=(width - 1 + 2 * edge_size))

        # Calculate indices to draw from flattened version of image batch
        dim2 = (width + 2 * edge_size)
        dim1 = (width + 2 * edge_size) * (height + 2 * edge_size)
        # Set offsets for each image in the batch
        base = dim1 * torch.arange(num_batch).type(tensor_type).cuda()
        base = base.view(-1, 1).repeat(1, height * width).view(-1)
        # One pixel shift in Y  direction equals dim2 shift in flattened array
        base_y0 = base + y0 * dim2
        # Add two versions of shifts in X direction separately
        idx_l = base_y0 + x0
        idx_r = base_y0 + x1

        # Sample pixels from images
        pix_l = im_flat.gather(1, idx_l.repeat(num_channels, 1).long())
        pix_r = im_flat.gather(1, idx_r.repeat(num_channels, 1).long())

        # Apply linear interpolation to account for fractional offsets
        weight_l = x1 - x
        weight_r = x - x0
        output = weight_l * pix_l + weight_r * pix_r

        # Reshape back into image batch and permute back to (N,C,H,W) shape
        output = output.view(num_channels, num_batch, height,
                            width).permute(1, 0, 2, 3)

        return output



    def LaplacianLayer(self, disp, img):
        # 4 direction Laplacian
        # laplacian_filter = torch.cuda.FloatTensor(
        #     [[0, 1, 0], [1, -4, 1], [0, 1, 0]]).view(1, 1, 3, 3)
        # 8 direction Laplacian
        laplacian_filter = torch.cuda.FloatTensor(
            [[1, 1, 1], [1, -8, 1], [1, 1, 1]]).view(1, 1, 3, 3)

        gray = self.getGrayImage(img)

        disp_lap = torch.nn.functional.conv2d(input=disp,
                                            weight=Variable(laplacian_filter),
                                            stride=1,
                                            padding=0)

        img_lap = torch.nn.functional.conv2d(input=gray,
                                            weight=Variable(laplacian_filter),
                                            stride=1,
                                            padding=0)

        disp_lap = torch.abs(disp_lap)
        img_lap = torch.abs(img_lap)

        weight_pixle = torch.exp(-img_lap, out=None)
        masking_disp_lap = weight_pixle * disp_lap

        # you can check the peformance
        if (True):
            save_image(gray/torch.max(gray), './result/gray.png')
            save_image(disp/torch.max(disp), './result/disp.png')
            save_image(disp_lap, './result/disp_lap.png')
            save_image(img/torch.max(img), './result/img.png')
            save_image(img_lap/torch.max(img_lap), './result/img_lap.png')
            save_image(masking_disp_lap, './result/masking_disp_lap.png')

        return torch.mean(masking_disp_lap)


    def SSIM1(self, x, y,window_size=3):
        C1 = 0.01 ** 2
        C2 = 0.03 ** 2
        clip_size = (window_size -1)/2

        mu_x = nn.functional.avg_pool2d(x, window_size, 1, padding=0)
        mu_y = nn.functional.avg_pool2d(y, window_size, 1, padding=0)

        x = x[:,:,clip_size:-clip_size,clip_size:-clip_size]
        y = y[:,:,clip_size:-clip_size,clip_size:-clip_size]

        sigma_x = nn.functional.avg_pool2d((x  - mu_x)**2, window_size, 1, padding=0)
        sigma_y = nn.functional.avg_pool2d((y - mu_y)**2, window_size, 1, padding=0)

        sigma_xy = (
            nn.functional.avg_pool2d((x- mu_x) * (y-mu_y), window_size, 1, padding=0)
        )

        mu_x = mu_x[:,:,clip_size:-clip_size,clip_size:-clip_size]
        mu_y = mu_y[:,:,clip_size:-clip_size,clip_size:-clip_size]

        SSIM_n = (2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)
        SSIM_d = (mu_x ** 2 + mu_y ** 2 + C1) * (sigma_x + sigma_y + C2)

        SSIM = SSIM_n / SSIM_d

        loss = torch.clamp((1 - SSIM) , 0, 2)
        if(True):
            save_image(loss, 'SSIM_GRAY1.png')

        return  torch.mean(loss)

    # TODO! this doesn't work find out reason
    # def SSIM2(self, x, y,window_size=3):
    #     C1 = 0.01 ** 2
    #     C2 = 0.03 ** 2
    #     clip_size = (window_size -1)/2

    #     mu_x = nn.functional.avg_pool2d(x, window_size, 1, padding=1)
    #     mu_y = nn.functional.avg_pool2d(y, window_size, 1, padding=1)
        

    #     print(x)
    #     print(x**2)


    #     sigma_x = nn.functional.avg_pool2d(x**2, window_size, 1, padding=1)-mu_x**2
    #     sigma_y = nn.functional.avg_pool2d(y**2, window_size, 1, padding=1)-mu_y**2

    #     print("sigma_x2=",torch.max(sigma_x))
    #     print("sigma_x2=",torch.min(sigma_x))

    #     print(sigma_x)

    #     # x = x[:,:,clip_size:-clip_size,clip_size:-clip_size]
    #     # y = y[:,:,clip_size:-clip_size,clip_size:-clip_size]
        
    #     sigma_xy = (
    #         nn.functional.avg_pool2d(x * y, window_size, 1, padding=1) - mu_x * mu_y
    #     )

    #     # mu_x = mu_x[:,:,clip_size:-clip_size,clip_size:-clip_size]
    #     # mu_y = mu_y[:,:,clip_size:-clip_size,clip_size:-clip_size]

    #     # sigma_x = sigma_x[:,:,clip_size:-clip_size,clip_size:-clip_size]
    #     # sigma_y = sigma_y[:,:,clip_size:-clip_size,clip_size:-clip_size]

    #     SSIM_n = (2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)
    #     SSIM_d = (mu_x ** 2 + mu_y ** 2 + C1) * (sigma_x + sigma_y + C2)

    #     SSIM = SSIM_n / SSIM_d

    #     # print("SSIM2=",torch.max(SSIM))
    #     # print("SSIM2=",torch.min(SSIM))

    #     loss = torch.clamp((1 - SSIM) , 0, 2)
    #     save_image(loss, 'SSIM_GRAY2.png')

    #     return  torch.mean(loss)


    def getGrayImage(self,rgbImg):
        gray = 0.114*rgbImg[:,0,:,:] + 0.587*rgbImg[:,1,:,:] + 0.299*rgbImg[:,2,:,:]
        gray = torch.unsqueeze(gray,1)
        return gray