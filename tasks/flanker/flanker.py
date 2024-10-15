from smile.common import *
from smile.scale import scale as s 
import config as config

@Subroutine
def Flanker(self, config, center_x, center_y, direction, row_shape = [5,3,1]):
    self.center_direction = direction
    self.stim_image = config.STIM_DIRECTORY + Ref(str, self.center_direction) + ".png"
    self.center_x = center_x
    self.center_y = center_y


    with Parallel():
        Background = Image(source = "ocean_background.png", size = (self.exp.screen.size[0] * 1.1, 
                                                                self.exp.screen.size[1] * 1.1),
                       allow_stretch = True, keep_ratio = False)
        center_image = Image(source = self.stim_image, center = (self.center_x, self.center_y), size = (100,100), allow_stretch = True, keep_ratio = False)
        for index,row in enumerate(row_shape):
            each_direction = (row-1) / 2
            row_starting_image_up = Image(source = self.stim_image, 
                                       center = (center_image.center_x, center_image.center_y + 100*index), size = (100,100), allow_stretch = True, keep_ratio = False)
            row_starting_image_down = Image(source = self.stim_image, 
                                       center = (center_image.center_x, center_image.center_y - 100*index), size = (100,100), allow_stretch = True, keep_ratio = False)
            for i in range(int(each_direction)):
                build_right_images_up = Image(source = self.stim_image, center_x = row_starting_image_up.center_x + 100*(i+1), 
                                           center_y = row_starting_image_up.center_y,size = (100,100),
                                           allow_stretch= True, keep_ratio = False)
                build_left_images_up = Image(source = self.stim_image, center_x = row_starting_image_up.center_x - 100*(i+1), 
                                           center_y = row_starting_image_up.center_y,size = (100,100),
                                           allow_stretch= True, keep_ratio = False)
                build_right_images_down = Image(source = self.stim_image, center_x = row_starting_image_down.center_x + 100*(i+1), 
                                           center_y = row_starting_image_down.center_y,size = (100,100),
                                           allow_stretch= True, keep_ratio = False)
                build_left_images_down = Image(source = self.stim_image, center_x = row_starting_image_down.center_x - 100*(i+1), 
                                           center_y = row_starting_image_down.center_y,size = (100,100),
                                           allow_stretch= True, keep_ratio = False)


        #         build_right_images = Image(source = self.stim_image, center_x = 
                                           
        #                                    , size = (100,100), allow_stretch = True, keep_ratio = False)


        #         build_right_images = Image(source = self.stim_image, center_x = center_image.center_x
                                           
        #                                    , size = (100,100), allow_stretch = True, keep_ratio = False)
        #         build_left_images =


        # for index,row in enumerate(row_shape):
        #     self.each_dir = (row - 1) / 2
        #     starting_image = Image(source = self.stim_image, center = (self.center_x, self.center_y + 100*index), size = (100,100), allow_stretch = True, keep_ratio = False)
        #     for i in range(self.each_dir):
        #         additional_image = Image(source = self.stim_image, center = (self.center_x, self.center_y), size = (100,100), allow_stretch = True, keep_ratio = False)



        # for i in range(row_shape):
        #     each_dir = (row_shape - 1) / 2
        #     self.center_x = self.center_x + 100
        #     self.center_y = self.center_y

        #     center_row = 


        #         row = Image(source = self.stim_image, center = (self.center_x, self.center_y), size = (100,100), allow_stretch = True, keep_ratio = False)
        #         self.center_x = self.center_x + 100
        #         self.center_y = self.center_y
        #starting_fish = Image(source = self.fish_image, center = (center_x, center_y))





        # with If(condition == '+'):
        #     self.fish_image = config.stim_directory + Ref(str, self.center_direction) + ".png"
        #     central_fish = Image(source = self.fish_image, center = (center_x, center_y))
        #     for row in shape:
        #         for i in range(row):

exp = Experiment()
Flanker(config, center_x = exp.screen.center_x , center_y = exp.screen.center_y, direction = "right")
exp.run()
    
