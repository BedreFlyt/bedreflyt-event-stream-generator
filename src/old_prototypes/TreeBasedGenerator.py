import numpy as np
from abc import ABC, abstractmethod

class Distribution(ABC):
    """Distribution class used in the generator to define a common interface"""
    def __init__(self):
        super().__init__()

    @abstractmethod
    def sample (self):
        """Samples from the distribution. Must be implemented in subclasses."""
        pass
    

class TreeBasedGenerator:
    """Class used for generating synthetic data based on a user-defined tree-structure of probabilistic distributions
    
    :param distribution_tree: dictionary tree structure of distributions of the type Distribution
    :param output_format: tuple of keys to be used for formatting the output
    :param output_sorting_function: function to be used for sorting the output, defaults to None
    """
    def __init__(self, distribution_tree=None, output_format=None, output_sorting_function=None):
        self.distribution_tree = distribution_tree
        self.output_format = output_format
        self.output_sorting_function=output_sorting_function

    def set_distribution_tree (self, distribution_tree):
        """Sets the distribution tree for the generator"""
        self.distribution_tree = distribution_tree
    
    def set_output_format (self, output_format):
        """Sets the output format for the generator"""
        self.output_format = output_format

    def set_output_sorting_function (self, output_sorting_function):
        """Sets the output sorting function for the generator"""
        self.output_sorting_function = output_sorting_function
    
    def generate_data(self):
        """Generates synthetic data based on the distribution tree, output format and sorting function"""
        res_tree = {}
        self.__sample_dist_tree_rec(self.distribution_tree, 1, res_tree)
        formatted_output = self.__format_output(res_tree)
        if self.output_sorting_function:
            formatted_output.sort(key=self.output_sorting_function)
        return formatted_output

    def __format_output (self, results_tree):
        """Formats the output based on the output format specified in the generator"""
        # Output format is not specified, return results tree
        if self.output_format == None: 
            print("Output format not specified, returns results tree")
            return results_tree
        # Output format is specified, return formatted output
        else:
            branches_to_be_merged = [] # List to hold branches that will be merged
            headers = self.output_format
            # Loop through each branch in the results tree and find the samples for each key in the output format
            for branch_key, branch  in results_tree.items():
                samples_divided_by_node_to_be_merged = []
                for header in headers[branch_key]:
                    output = self.__find_result_from_header_rec(header, branch)
                    samples_divided_by_node_to_be_merged.append(output)
                
                # Convert list of list into a list of tuples: LL: [[1,2,3],[4,5,6]] -> LT: [(1,4),(2,5),(3,6)]
                merged_samples = list(zip(*samples_divided_by_node_to_be_merged))
                branches_to_be_merged.append(merged_samples)
            
            # Merge all branches into a single list
            # all_branches_merged_output = np.concatenate(branches_to_be_merged).tolist()
            all_branches_merged_output = [inner for outer in branches_to_be_merged for inner in outer]
            return all_branches_merged_output
    
    def __find_result_from_header_rec(self, key, res_tree=None):
        """Recursively searches for results in the results tree based on the key provided"""
        if res_tree is None:
            raise ValueError("res_tree must be provided when calling __find_result_from_key_rec")

        results = []

        for k, v in res_tree.items():
            if k == key and isinstance(v, dict) and "res" in v:
                results.extend(v["res"])
            elif isinstance(v, dict):
                # Recursively search nested dictionaries
                results.extend(self.__find_result_from_header_rec(key, v))

        return results
            
    
    def __sample_dist_tree_rec(self, dist_tree, prev_res, results_tree={}):    
        """Recursively samples from the distribution tree and updates the results tree"""
        
        # Get distribution keys by removing special keys
        dist_keys = list(dist_tree.keys())
        if "dist" in dist_keys: dist_keys.remove("dist")
        if "no_sample_aggregation" in dist_keys: dist_keys.remove("no_sample_aggregation")

        # Loop through distribution keys
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