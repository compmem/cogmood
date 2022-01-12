
from random import shuffle
import copy

def gen_order(config):
   blocks = []
   these_tasks = copy.deepcopy(config.TASKS)
   shuffle(these_tasks)
   for i in range(config.NUM_REPS):
       tasks = copy.deepcopy(these_tasks)
       for task_block in tasks:
           if config.SHUFFLE_TASKS:
               shuffle(task_block)
               if len(blocks) > 0:
                   while((blocks[-1][-1] == task_block[0]) or task_block in blocks):
                       shuffle(task_block)
           blocks.append(task_block)
   return blocks
