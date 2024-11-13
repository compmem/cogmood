import random
from math import cos, sin, sqrt, pi, radians


# list generation
def gen_fblocks(config):
    flanker_blocks = []
    for blo in range(config.NUM_BLOCKS):
        for b in range(config.NUM_REPS):
            temp_block = []
            for i in range(config.NUM_TRIALS):
                for l in range(config.NUM_LOCS):
                    temp_trial = {'loc_x':cos(radians((360./config.NUM_LOCS)*l)),
                                  'loc_y':sin(radians((360./config.NUM_LOCS)*l)),
                                  }
                    for s in config.CONDITIONS:
                        trial = temp_trial.copy()
                        if s['dir'] == "left":
                            key_resp = config.RESP_KEYS[0]
                        else:
                            key_resp = config.RESP_KEYS[-1]
                        # MIXED EASY RIGHT
                        trial.update({'condition': s['condition'],
                                      'dir': s['dir'],
                                      'corr_resp': key_resp
                                      })
                        temp_block.append(trial.copy())
            random.shuffle(temp_block)
            flanker_blocks.append(temp_block)
    return flanker_blocks
