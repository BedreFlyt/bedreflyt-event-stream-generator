import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from abc import ABC, abstractmethod

class Distribution(ABC):
    """Distribution class used in the generator to define common interface"""
    def __init__(self):
        super().__init__()

    @abstractmethod
    def sample (self):
        pass
    



class Generator:
    """..."""
    def __init__(self, time_step_seconds=1, distribution_tree=None, run_in_real_time=False):
        self.__results_tree = None # To hold the results in a tree structure
        self.time_step_seconds = time_step_seconds
        self.distribution_tree = distribution_tree
        self.run_in_real_time = run_in_real_time

    def generate_results(self):
        """..."""
        res_tree = {}
        self.__sample_dist_tree_rec(self.distribution_tree, 1, res_tree)
        print(res_tree)

    
    def __sample_dist_tree_rec(self, dist_tree, prev_res, results_tree={}):    
         # Sample recursively in sub distributions
        # - Get Sub Distributions Keys
        dist_keys = list(dist_tree.keys())
        if "dist" in dist_keys: dist_keys.remove("dist")
        if "no_sample_aggregation" in dist_keys: dist_keys.remove("no_sample_aggregation")

        # print(dist_tree)

        # - distributions recursively
        for dist_key in dist_keys:
            # Get distribution tree
            sub_dist_tree = dist_tree[dist_key]
            sub_dist_model = sub_dist_tree["dist"]
            no_samples_aggregation = sub_dist_tree["no_sample_aggregation"]
            no_samples = no_samples_aggregation(prev_res)

            # Sample subdistributions and update results tree
            if isinstance(sub_dist_model, Distribution):
                res = [sub_dist_model.sample() for _ in range(no_samples)]
            else:
                res = [sub_dist_model[prev_res[i]].sample() for i in range(no_samples)]
            
            sub_sub_res_tree = {"res": res}
            sub_res_tree = {dist_key: sub_sub_res_tree}            
            
            # sample sub distribution
            self.__sample_dist_tree_rec(sub_dist_tree, res, sub_sub_res_tree)

            # update results
            results_tree.update(sub_res_tree)

if __name__ == "__main__":
    
    class NumberOfPatientsDistribution(Distribution):
        def __init__(self):
            super().__init__()
            self.values = [2, 3, 4, 5]
            self.probabilities = [0.1, 0.2, 0.3, 0.4]

        def sample(self):
            return int(np.random.choice(self.values, p=self.probabilities))

    num_patients_dist: Distribution = NumberOfPatientsDistribution()

    class MaleDiseasesDistribution(Distribution):
        def __init__(self):
            super().__init__()
            self.values = ["Disease A", "Disease B", "Disease C", "Disease D"]
            self.probabilities = [0.1, 0.2, 0.3, 0.4]

        def sample(self):
            return str(np.random.choice(self.values, p=self.probabilities))
    
    male_diseases_dist: Distribution = MaleDiseasesDistribution()

    class FemaleDiseasesDistribution(Distribution):
        def __init__(self):
            super().__init__()
            self.values = ["Disease F", "Disease G", "Disease H", "Disease I"]
            self.probabilities = [0.4, 0.3, 0.2, 0.1]

        def sample(self):
            return str(np.random.choice(self.values, p=self.probabilities))

    female_diseases_dist: Distribution = FemaleDiseasesDistribution()

    class GenderDistribution(Distribution):
        def __init__(self):
            super().__init__()
            self.values = ["male", "female"]
            self.probabilities = [0.5, 0.5]

        def sample(self):
            return str(np.random.choice(self.values, p=self.probabilities))

    gender_dist: Distribution = GenderDistribution()

    DistributionTreeNoPatients = {
        "number_of_patients": {
            "dist": num_patients_dist,
            "no_sample_aggregation": lambda x: x,
            "gender": {
                "dist": gender_dist,
                "no_sample_aggregation": lambda x: x[0],
                "disease": {
                    "dist": {
                        "male": male_diseases_dist,
                        "female": female_diseases_dist
                    },
                    "no_sample_aggregation": len,
                }
        }
        },
    }

    class NumberOfPatientsDuringADayDistribution(Distribution):
        def __init__(self):
            super().__init__()

        def sample(self):
            return int(np.random.normal(300, 30))

    num_patients_per_day_dist: Distribution = NumberOfPatientsDuringADayDistribution()

    # class ArrivalTime(Distribution):
    #     def __init__(self):
    #         super().__init__()
    #         self.values = ["8-12", "12-16", "16-20", "20-24"]
    #         self.probabilities = [0.1, 0.3, 0.4, 0.2]

    #     def sample(self):
    #         return str(np.random.choice(self.values, p=self.probabilities))

    # arrival_time: Distribution = ArrivalTime()
    import numpy as np
    from datetime import time
    import random

    class ArrivalTime(Distribution):
        def __init__(self):
            super().__init__()
            self.intervals = [(8, 12), (12, 16), (16, 20), (20, 24)]
            self.probabilities = [0.1, 0.3, 0.4, 0.2]

        def sample(self) -> str:
            start, end = random.choices(self.intervals, weights=self.probabilities, k=1)[0]
            sampled = np.random.uniform(start, end)
            h, rem = divmod(sampled * 3600, 3600)
            m, s = divmod(rem, 60)
            return time(int(h), int(m), int(s)).strftime("%H:%M:%S")
        
    arrival_time: Distribution = ArrivalTime()

    DistributionTreeNoPatientsPrDay = {
        "number_of_patients": {
            "dist": num_patients_per_day_dist,
            "no_sample_aggregation": lambda x: x,
            "arrival_time": {
                "dist": arrival_time,
                "no_sample_aggregation": lambda x: x[0],
            },
            "gender": {
                "dist": gender_dist,
                "no_sample_aggregation": lambda x: x[0],
                "disease": {
                    "dist": {
                        "male": male_diseases_dist,
                        "female": female_diseases_dist
                    },
                    "no_sample_aggregation": len,
                }
        }
        },
    }

    # for all elements in the distribution tree (top nodes)
    # sample its distribution

    generator = Generator(1, DistributionTreeNoPatientsPrDay)
    generator.generate_results()


    # DistributionTreeExample = {
    #     "number_of_patients": {
    #         "dist": num_patients_dist,
    #         "gender": {
    #             "dist": gender_dist,
    #             "disease": {
    #                 "dist_Male": male_diseases_dist,
    #                 "dist_Female": female_diseases_dist
    #             }
    #     }
    #     },
    # }