
DistributionTreeExample = {
        "dist": "num_patients_dist",
        "sub_dist1": {
            "dist": "gender_dist",
            "conditioned_sub1": {
                "Male": "male_diseaes_dist",
                "Female": "f"
            }
        },
        "sub_dist_999": 999
    }

sub_dist_keys = [key for key in DistributionTreeExample if key.startswith("sub_dist")]

print(sub_dist_keys)