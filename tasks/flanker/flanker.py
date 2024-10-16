from smile.common import *
from smile.scale import scale as s 
import config as config

@Subroutine
def Flanker(self, config, center_x, center_y, direction, condition, num_layers = 2):
    #num_layers describes how many layers there are in the diamond, for example 2 layers means that the diamond
    #is an array of 1,3,5,3,1
    self.center_direction = direction
    self.center_image = config.STIM_DIRECTORY + Ref(str, self.center_direction) + ".png"
    self.center_x = center_x
    self.center_y = center_y

    with If(condition == "+"):
        self.stim_image = self.center_image

    with Parallel():
        Background = Image(source = "ocean_background.png", size = (self.exp.screen.size[0] * 1.1, 
                                                                self.exp.screen.size[1] * 1.1),
                       allow_stretch = True, keep_ratio = False)
        center_image = Image(source = self.center_image, center = (self.center_x, self.center_y), size = (100,100), allow_stretch = True, keep_ratio = False)
        for i in range(num_layers):
            add_right = Image(source = self.stim_image, size = (100,100),
                              keep_ratio = False, allow_stretch = True,
                              center = (self.center_x + 100*(i+1), self.center_y))
            add_left = Image(source = self.stim_image, size = (100,100),
                             keep_ratio = False, allow_stretch = True,
                             center = (self.center_x - 100*(i+1), self.center_y))
            add_up = Image(source = self.stim_image, size = (100,100),
                             keep_ratio = False, allow_stretch = True,
                             center = (self.center_x, self.center_y + 100*(i+1)))
            add_down = Image(source = self.stim_image, size = (100,100),
                             keep_ratio = False, allow_stretch = True,
                             center = (self.center_x, self.center_y - 100*(i+1)))
            # self.stim_image = config.STIM_DIRECTORY + Ref(str, self.center_direction) + ".png"
            #Need to add in actual stim rules here
            for mult in range(num_layers - (i+1)):
                add_right_up = Image(source = self.stim_image, size = (100,100),
                            keep_ratio = False, allow_stretch = True,
                            center = (add_right.center_x, add_right.center_y + 100*(mult+1)))
                add_right_down = Image(source = self.stim_image, size = (100,100),
                            keep_ratio = False, allow_stretch = True,
                            center = (add_right.center_x, add_right.center_y - 100*(mult+1)))
                add_left_up = Image(source = self.stim_image, size = (100,100),
                            keep_ratio = False, allow_stretch = True,
                            center = (add_left.center_x, add_left.center_y + 100*(mult+1)))
                add_left_down = Image(source = self.stim_image, size = (100,100),
                            keep_ratio = False, allow_stretch = True,
                            center = (add_left.center_x, add_left.center_y - 100*(mult+1)))








            # self.layer = 1
            # self.leftover = num_layers - Ref(int,self.layer)
            # for i in range(Ref(int,lef),0,-1):
            #     add_right_up = Image(source = self.stim_image, size = (100,100),
            #                 keep_ratio = False, allow_stretch = True,
            #                 center = (add_right.center_x, add_right.center_y + 100*(i+1)))
            # self.layer = self.layer + 1



            #     add_right_up = Image(source = self.stim_image, size = (100,100),
            #                 keep_ratio = False, allow_stretch = True,
            #                 center = (add_right.center_x, add_right.center_y + 100*(i+1)))
            # add_right_down = Image(source = self.stim_image, size = (100,100),
            #                 keep_ratio = False, allow_stretch = True,
            #                 center = (self.center_x + 100*(i+1), self.center_y - 100*(i+1)))
            # add_left_up = Image(source = self.stim_image, size = (100,100),
            #                 keep_ratio = False, allow_stretch = True,
            #                 center = (self.center_x - 100*(i+1), self.center_y + 100*(i+1)))
            # add_left_down = Image(source = self.stim_image, size = (100,100),
            #                 keep_ratio = False, allow_stretch = True,
            #                 center = (self.center_x - 100*(i+1), self.center_y - 100*(i+1)))

            
            


            
            # all_directions = [add_right, add_left, add_up, add_down]
            # for index,direction in enumerate(all_directions):
            #     copied_list = all_directions.copy().pop(index)
            #         new_image = Image(source = self.center_image, size = (100,100),
            #                  keep_ratio = False, allow_stretch = True,
            #                  center = (direction.center, direction.center - 100*(i+1)))




            # for direction in all_directions:
            #     for image in all_direction_images:
            #         if direction in all_direction_images:
            #     new_image = Image(source = self.center_image, )




        # for index,row in enumerate(row_shape):
        #     each_direction = (row-1) / 2
        #     row_starting_image_up = Image(source = self.stim_image, 
        #                                center = (center_image.center_x, center_image.center_y + 100*index), size = (100,100), allow_stretch = True, keep_ratio = False)
        #     row_starting_image_down = Image(source = self.stim_image, 
        #                                center = (center_image.center_x, center_image.center_y - 100*index), size = (100,100), allow_stretch = True, keep_ratio = False)
        #     for i in range(int(each_direction)):
        #         build_right_images_up = Image(source = self.stim_image, center_x = row_starting_image_up.center_x + 100*(i+1), 
        #                                    center_y = row_starting_image_up.center_y,size = (100,100),
        #                                    allow_stretch= True, keep_ratio = False)
        #         build_left_images_up = Image(source = self.stim_image, center_x = row_starting_image_up.center_x - 100*(i+1), 
        #                                    center_y = row_starting_image_up.center_y,size = (100,100),
        #                                    allow_stretch= True, keep_ratio = False)
        #         build_right_images_down = Image(source = self.stim_image, center_x = row_starting_image_down.center_x + 100*(i+1), 
        #                                    center_y = row_starting_image_down.center_y,size = (100,100),
        #                                    allow_stretch= True, keep_ratio = False)
        #         build_left_images_down = Image(source = self.stim_image, center_x = row_starting_image_down.center_x - 100*(i+1), 
        #                                    center_y = row_starting_image_down.center_y,size = (100,100),
        #                                    allow_stretch= True, keep_ratio = False)


exp = Experiment()
Flanker(config, center_x = exp.screen.center_x , center_y = exp.screen.center_y, direction = "left", condition = "+")
exp.run()
    
