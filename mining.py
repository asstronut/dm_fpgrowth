from mlxtend.frequent_patterns import association_rules, fpgrowth


def perform_rule_calculation(transact_items_matrix, min_support=0.001):
    """
    desc: this function performs the association rule calculation 
    @params:
        - transact_items_matrix: the transaction X Items matrix
        - rule_type: 
                    - apriori or Growth algorithms (default="fpgrowth")

        - min_support: minimum support threshold value (default = 0.001)

    @returns:
        - the matrix containing 3 columns:
            - support: support values for each combination of items
            - itemsets: the combination of items
            - number_of_items: the number of items in each combination of items

        - the excution time for the corresponding algorithm

    """
    start_time = 0
    # total_execution = 0

    # if (not rule_type == "fpgrowth"):
    #     # start_time = time.time()
    #     rule_items = apriori(transact_items_matrix,
    #                          min_support=min_support,
    #                          use_colnames=True)
    #     # total_execution = time.time() - start_time
    #     print("Computed Apriori!")

    # else:
    # start_time = time.time()
    rule_items = fpgrowth(transact_items_matrix,
                          min_support=min_support,
                          use_colnames=True)
    # total_execution = time.time() - start_time
    # print("Computed Fp Growth!")

    rule_items['number_of_items'] = rule_items['itemsets'].apply(
        lambda x: len(x))

    return rule_items


def compute_association_rule(rule_matrix, metric="lift", min_thresh=1):
    """
    @desc: Compute the final association rule
    @params:
        - rule_matrix: the corresponding algorithms matrix
        - metric: the metric to be used (default is lift)
        - min_thresh: the minimum threshold (default is 1)

    @returns:
        - rules: all the information for each transaction satisfying the given metric & threshold
    """
    rules = association_rules(rule_matrix,
                              metric=metric,
                              min_threshold=min_thresh)

    return rules
