

def cp_or_mdj(docket_number):
    """ Is `docket_number` a CP docket, or a MDJ docket? """
    if len(docket_number) == 21:
        return "CP"
    if len(docket_number) == 24:
        return "MDJ"
    return None
