import json
import numpy as np
from pickle import FALSE, TRUE
import pandas as pd
from scipy.stats import  nchypergeom_wallenius



#count number of red cards in array
def is_red(name):
    return any(substring in name for substring in ["hearts","diamonds"])

vec_is_red = np.vectorize(is_red)

class GameGenerator:
    def __init__(self, nr_game_batches=20, nr_game_batches_calibration=60):
        self.nr_games = nr_game_batches
        self.nr_games_calibration = nr_game_batches_calibration

        self.rng = np.random.default_rng(42)
        self.total_count = 156
        self.total_red_count = 78
        self.nr_total = 65
        self.ai_total = 13
        self.mult= 5
        self.shape = (5,13)
        self.shape_center = (3,7)
        self.row = (self.shape[0]-self.shape_center[0])//2
        self.col = (self.shape[1]-self.shape_center[1])//2
        self.nr_shown = 21
        self.center_odds = 1
        self.center_odds_other= {"level_B": 4 , "level_A": 4,"level_C": 1} # similar utility, not much disalignment
        self.var_per_bin = {1:8, 2:8, 3:8, 4:8, 5:8, 6:8, 7:8, 8:8, 9:8, 10:8, 11:8, 12:8}

        self.games_level_B = []
        self.games_level_C = []
        self.games_level_A = []
        self.attention = []
        self.games_level_B_cal = []
        
        self.create_all_games()

    # returns AI confidence in terms of percentage
    def get_AI_conf(self, ai_reds):
        return round(ai_reds/self.ai_total * 100)

    # returns bias for sampling in terms of odds
    def bias(self, nr_reds, nr_ai_reds, level):
        if level=="level_C" or ((nr_reds <= nr_ai_reds*self.mult+1) and (nr_reds >= nr_ai_reds*self.mult-1)):
            return 1
        elif nr_reds > nr_ai_reds*self.mult+1:
            if level=="level_B":
                return self.center_odds/self.center_odds_other[level]
            else:
                return self.center_odds_other[level]/self.center_odds
        elif nr_reds < nr_ai_reds*self.mult-1:
            if level=="level_B":
                return self.center_odds_other[level]/self.center_odds
            else:
                return self.center_odds/self.center_odds_other[level]

    
    #sample shown cards and create a grid with hidden and shown cards
    #input array: array of cards, reds: number of red cards, odds: bias for sampling
    def get_grid(self, array, reds, odds):
        #sample number of reds in shown cards according to a (wallenius) hypergeometric distribution
        reds_shown = nchypergeom_wallenius.rvs(self.nr_total, reds, self.nr_shown, odds=odds, size=1)[0]
        #get red cards from the front of array
        center_array = array[:reds_shown]
        #get black cards from the back of array
        if center_array.size != self.nr_shown:
            center_array = np.concatenate((center_array, array[(-self.nr_shown+reds_shown):]))
        #permute shown cards and create grid
        center_grid = self.rng.permutation(center_array).reshape(self.shape_center) 
        #add hidden cards around shown cards
        full_grid = np.repeat('img/img_card_back.png', self.nr_total).reshape(self.shape).astype('<U40')
        full_grid[self.row:self.row+self.shape_center[0], self.col:self.col+self.shape_center[1]] = center_grid
        #check if the number of red cards in the grid is correct
        if (vec_is_red(full_grid).sum()!=reds_shown):
            print("Error")

        return full_grid, int(reds_shown)


    #create game dictionary for json file
    def create_game_dict(self, id, batch, grid, array, nr_reds, nr_ai_reds, nr_reds_shown):
        return {
            "id": id,
            "batch": batch,
            "game": grid.tolist(),
            "cards": array.tolist(),
            "nr_reds": nr_reds,
            "nr_total": self.nr_total,
            "AI_reds": nr_ai_reds,
            "AI_total": self.ai_total,
            "AI_conf": self.get_AI_conf(nr_ai_reds),
            "nr_reds_shown": nr_reds_shown,
            "nr_shown": self.nr_shown
        }

    # create a game for given number of reds and level
    def create_game(self, id, batch, nr_reds, nr_ai_reds, game_pile, shuffle=TRUE, level="level_B"):
        # # get red and black cards according to the number of reds in the game
        # array_red = self.rng.choice(reds, nr_reds, replace=False) 
        # array_black = self.rng.choice(blacks, self.nr_total - nr_reds, replace=False)
        # array of game cards' name
        # game_pile = np.concatenate([array_red, array_black])
        # grid for attention game
        if (nr_reds in [0, self.nr_total]):
            shuffle = FALSE
        if shuffle == FALSE:
            full_grid = np.repeat('img/img_card_back.png', self.nr_total).reshape(self.shape).astype('<U40')
            full_grid[self.row:self.row+self.shape_center[0], self.col:self.col+self.shape_center[1] ] = game_pile.reshape(self.shape)[self.row:self.row+self.shape_center[0], self.col:self.col+self.shape_center[1]] 
            nr_reds_shown = int(np.vectorize(lambda name: any(substring in name for substring in ["hearts","diamonds"]))(full_grid).sum())
            return self.create_game_dict(id, batch, full_grid, game_pile, nr_reds, nr_ai_reds, nr_reds_shown)
 
        # generate grid for level sampling shown cards according to odds
        odds = self.bias(nr_reds, nr_ai_reds, level)
        full_grid, nr_reds_shown = self.get_grid(game_pile, nr_reds, odds)
        return self.create_game_dict(id, batch, full_grid, game_pile, nr_reds, nr_ai_reds, nr_reds_shown)

    # create a list of games for each bin
    def create_game_per_bin(self,reds, blacks):

        ai_bin = []
        true_bin = []
        #for each AI bin create nine cells, three around the given AI confidence, six around the given AI confidence +- variance of AI bin
        for nr_ai_reds in range(1,13):
            # max variance per bin
            max_var = (self.mult-1)*min(nr_ai_reds,13-nr_ai_reds)
            # minimum of max and given variance
            var = min(self.var_per_bin[nr_ai_reds], max_var)

            # compute cells
            rmin = self.mult*nr_ai_reds-var
            rmax = self.mult*nr_ai_reds+var

            #add created cells in this bin to the list of cells
            ai_bin += np.full(2,nr_ai_reds).tolist()
            true_bin += [rmin, rmax]

        #get cells probabilities for each level
        df_bins = pd.DataFrame({'AI_reds': ai_bin, "true_reds": true_bin})

        #generate test games in each level
        games_list ={"level_B": [], "level_C": [], "level_A": []}
        # id_offset={"level_B": 0, "level_C": 0, "level_A": 0}


        #generate game according to cell properties
        id=-1
        for _ in range(self.nr_games):
            trial_games = {"level_B": [], "level_C": [], "level_A": []}
            for _, bin in df_bins.iterrows():
                id+=1
                # get red and black cards according to the number of reds in the game
                nr_reds = int(bin["true_reds"])
                array_red = self.rng.choice(reds, nr_reds, replace=False) 
                array_black = self.rng.choice(blacks, self.nr_total - nr_reds, replace=False)
                game_pile = np.concatenate([array_red, array_black])
                for level in ["level_B", "level_C", "level_A"]:
                    #create game
                    games = self.create_game( id, "game", nr_reds ,int(bin["AI_reds"]), game_pile, level=level) #id_offset[level] +
                    trial_games[level].append(games)
                
                # id_offset[level] += id
            games_list["level_A"] += [trial_games["level_A"]]
            games_list["level_B"] += [trial_games["level_B"]]
            games_list["level_C"] += [trial_games["level_C"]]

        #generate games for calibration data
        calibration_data = []
        #generate game according to cell properties
        for _ in range(self.nr_games_calibration):
            trial_games = []
            for _,bin in df_bins.iterrows():
                # get red and black cards according to the number of reds in the game
                nr_reds = int(bin["true_reds"])
                array_red = self.rng.choice(reds, nr_reds, replace=False) 
                array_black = self.rng.choice(blacks, self.nr_total - nr_reds, replace=False)
                game_pile = np.concatenate([array_red, array_black])
                games = self.create_game( id, "calibration", nr_reds, int(bin["AI_reds"]), game_pile, level="level_B") 
                trial_games.append(games)
                id+=1

            # id_offset["level_B"] += id
            calibration_data += [trial_games]

        return (games_list["level_B"], games_list["level_C"], games_list["level_A"], calibration_data)

    #writes games to json file
    def write_json_to_file(self, json_object, filename):
        with open(filename, "w") as outfile:
            outfile.write(json_object)

    def write_to_folder(self, games, level):
        for index, trial in enumerate(games):
            # print(trial)
            trial_json = json.dumps(trial, indent=4, default=str)
            self.write_json_to_file(trial_json,"./materials/games_"+level+"/"+str(index)+".json")


    def create_all_games(self):

        # Opening JSON file
        f = open('./materials/cards.json')
        
        # returns JSON object as a dictionary
        cards = json.load(f)
        # triple the amount of cards (three standard decks)
        cards = cards + cards + cards
        # filter red and black cards
        reds = [ card for card in cards if any(substring in card for substring in ["hearts","diamonds"])]
        blacks = [ card for card in cards if any(substring in card for substring in ["clubs","spades"])]

        # create attention games
        red_grid = self.create_game(-1,"attention",self.nr_total, self.ai_total, np.array(reds[:self.nr_total]), shuffle=FALSE)
        black_grid = self.create_game(-2,"attention",0, 0, np.array(blacks[:self.nr_total]), shuffle=FALSE)
        quarter = int((self.mult-2) * self.nr_total/5)
        quarter_grid = self.create_game(-3,"attention",quarter,round((self.mult-2) * self.ai_total/5 + self.rng.integers(-1, 1)), np.concatenate([reds[:quarter], blacks[:self.nr_total-quarter]]), shuffle=FALSE)
        half = round(self.nr_total/2)
        half_grid = self.create_game(-4,"attention",half,round(self.ai_total/2), np.concatenate([reds[:half], blacks[:self.nr_total-half]]), shuffle=FALSE)

        # create level games
        games_level_B, games_level_C, games_level_A, games_level_B_calibration = self.create_game_per_bin(reds, blacks)

        # create json from dictionary
        self.write_to_folder(games_level_A, "level_A")
        self.write_to_folder(games_level_B, "level_B")
        self.write_to_folder(games_level_C, "level_C") 
        self.write_to_folder(games_level_B_calibration, "level_B_cal")

        attention = json.dumps([red_grid, black_grid, quarter_grid, half_grid], indent=4)
        self.write_json_to_file(attention, "./materials/attention_tests.json")

        self.games_level_B = sum(games_level_B, [])
        self.games_level_C = sum(games_level_C,[]) 
        self.games_level_A = sum(games_level_A, [])
        self.attention = attention
        self.games_level_B_cal = sum(games_level_B_calibration,[])

    # generate URLs for prolific to each game batch
    def create_urls(self):
        url_list = []
        for level in ["A", "B", "C"]:
            study_website = "https://hac-experiment.mpi-sws.org/?LEVEL="+level+"_cal&GAME_BATCH="
            url_list += [{"url": study_website+str(i)} for i in range(0,self.nr_games)]

            if level == "B":
                url_list_cal = [{"url": study_website+str(i)} for i in range(0,self.nr_games_calibration)]
                pd.DataFrame(url_list_cal).to_csv("./prolific/urls_cal.csv", index=False)

        pd.DataFrame(url_list).to_csv("./prolific/urls.csv", index=False)


    def get_games_level_B(self):
        return self.games_level_B
    
    def get_games_level_B_cal(self):
        return self.games_level_B_cal
    
    def get_games_level_A(self):
        return self.games_level_A
    
    def get_games_level_C(self):
        return self.games_level_C
    
    def get_games_attention(self):
        return self.attention
