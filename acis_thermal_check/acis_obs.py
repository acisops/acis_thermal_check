import numpy as np
from acis_thermal_check.utils import mylog
from kadi.commands.states import decode_power


def who_in_fp(simpos=80655):
    """
    Returns a string telling you which instrument is in
    the Focal Plane. "launchlock" is returned because that's a
    position we never expect to see the sim in - it's an indicator
    to the user that there's a problem.

    Also, The ranges for detector sections use the max and min hard
    stop locations, and they also split the difference between "I"
    and "S" for each instrument.

          input: - TSC position (simpos) - INTEGER

          output - String indicating what is in the focal plane
                   "launchlock" - default
                   "ACIS-I"
                   "ACIS-S"
                   "HRC-I"
                   "HRC-S"
    """
    is_in_the_fp = 'launchlock'

    #  Set the value of is_in_the_fp to the appropriate value. It will default
    #  to "launchlock" if no value matches
    if 104839 >= simpos >= 82109:
        is_in_the_fp = 'ACIS-I'
    elif 82108 >= simpos >= 70736:
        is_in_the_fp = 'ACIS-S'
    elif -20000 >= simpos >= -86147:
        is_in_the_fp = 'HRC-I'
    elif -86148 >= simpos >= -104362:
        is_in_the_fp = 'HRC-S'

    #  return the string indicating which instrument is in the Focal Plane
    return is_in_the_fp


def fetch_ocat_data(obsid_list):
    """
    Take a list of obsids and return the following data from
    the obscat for each: grating status, CCD count, if S3 is on,
    and the number of expected counts

    Parameters
    ----------
    obsid_list : list of ints
        The obsids to get the obscat data from.

    Returns
    -------
    A dict of NumPy arrays of the above properties.
    """
    import requests
    from ska_helpers.retry import retry_call, RetryError
    from astropy.io import ascii
    warn = "Could not get the table from the Obscat to " \
           "determine which observations can go to -109 C. " \
           "Any violations of eligible observations should " \
           "be hand-checked."
    # Only bother with this check if obsids are found
    if len(obsid_list) > 0:
        # The following uses a request call to the obscat which explicitly
        # asks for text formatting so that the output can be ingested into
        # an AstroPy table.
        urlbase = "https://cda.harvard.edu/srservices/ocatDetails.do?format=text"
        obsid_list = ",".join([str(obsid) for obsid in obsid_list])
        params = {"obsid": obsid_list}
        # First fetch the information from the obsid itself
        got_table = True
        try:
            resp = retry_call(requests.get, [urlbase], {"params": params}, 
                              tries=4, delay=1)
        except (requests.ConnectionError, RetryError):
            got_table = False
        else:
            if not resp.ok:
                got_table = False
    else:
        warn = "No obsids to check, may be a vehicle load--please check " \
               "if not."
        got_table = False
    if got_table:
        tab = ascii.read(resp.text, header_start=0, data_start=2)
        tab.sort("OBSID")
        # Now we have to find all of the obsids in each sequence and then
        # compute the complete exposure for each sequence
        seq_nums = np.unique([str(sn) for sn in tab["SEQ_NUM"].data.astype("str") 
                              if sn != " "])
        seq_num_list = ",".join(seq_nums)
        obsids = tab["OBSID"].data.astype("int")
        cnt_rate = tab["EST_CNT_RATE"].data.astype("float64")
        params = {"seqNum": seq_num_list}
        got_seq_table = True
        try:
            resp = retry_call(requests.get, [urlbase], {"params": params},
                              tries=4, delay=1)
        except(requests.ConnectionError, RetryError):
            got_seq_table = False
        else:
            if not resp.ok:
                got_seq_table = False
        if not got_seq_table:
            # We weren't able to get a valid sequence table for some
            # reason, so we cannot check for -109 data, but we proceed
            # with the rest of the review regardless
            mylog.warning(warn)
            return None
        tab_seq = ascii.read(resp.text, header_start=0, data_start=2)
        app_exp = np.zeros_like(cnt_rate)
        seq_nums = tab_seq["SEQ_NUM"].data.astype("str")
        for i, row in enumerate(tab):
            sn = str(row["SEQ_NUM"])
            if sn == " ":
                continue
            j = np.where(sn == seq_nums)[0]
            app_exp[i] += np.float64(tab_seq["APP_EXP"][j]).sum()
        app_exp *= 1000.0
        table_dict = {"obsid": np.array(obsids),
                      "grating": tab["GRAT"].data,
                      "cnt_rate": cnt_rate,
                      "app_exp": app_exp}
    else:
        # We weren't able to get a valid table for some reason, so
        # we cannot check for -109 data, but we proceed with the
        # rest of the review regardless
        mylog.warning(warn)
        table_dict = None
    return table_dict


def find_obsid_intervals(cmd_states, load_start):
    """
    User reads the SKA commanded states archive, via
    a call to the SKA kadi.commands.states.get_states, 
    between the user specified START and STOP times.

    Problem is, ALL commanded states that were stored
    in the archive will be returned. So then you call:

        find_obsid_intervals(cmd_states)

    And this will find the obsid intervals.
    What this program does is to extract the time interval for
    each OBSID. Said interval start is defined by a
    startScience comment, and the interval end is
    defined by the first stopScience command that follows.

    When the interval has been found,
    a dict element is created from the value of
    states data at the time point of the first NPNT
    line seen - *minus* the trans_keys, tstart and tstop
    times. The values of datestart and datestop are
    the XTZ00000 and AA000000 times. This dict
    is appended to a Master list of all obsid intervals
    and this list is returned.

    Notes: The obsid filtering method includes the
           configuration from the last OBSID, through
           a setup for the present OBSID, through the
           XTZ - AA000, down to the power down.

            - This might show a cooling from the
              last config, temp changes due to some
              possible maneuvering, past shutdown
    """
    #
    # Some inits
    #

    # a little initialization
    firstpow = False
    xtztime = None

    # EXTRACTING THE OBSERVATIONS
    #
    # Find the first line with a WSPOW00000 in it. This is the start of
    # the interval. Then get the first XTZ line, the NPNT line, the
    # AA000000 line, and lastly the next WSPOW00000 line.
    # This constitutes one observation.

    obsid_interval_list = []

    for eachstate in cmd_states:

        # Make sure we skip maneuver obsids explicitly
        if 60000 > eachstate['obsid'] >= 38001:
            continue

        # Only check states which are at least partially
        # within the load being reviewed
        if eachstate["tstop"] < load_start:
            continue

        pow_cmd = eachstate['power_cmd']

        # is this the first WSPOW of the interval?
        if pow_cmd in ['WSPOW00000', 'WSVIDALLDN'] and not firstpow:
            firstpow = True
            datestart = eachstate['datestart']
            tstart = eachstate['tstart']

        # Process the power command which turns things on
        if pow_cmd.startswith("WSPOW") and pow_cmd != 'WSPOW00000' \
            and firstpow:
            ccds = decode_power(pow_cmd)['ccds'].replace(" ", ",")[:-1]

        # Process the first XTZ0000005 line you see
        if pow_cmd in ['XTZ0000005', 'XCZ0000005'] and \
                (xtztime is None and firstpow):
            xtztime = eachstate['tstart']
            # MUST fix the instrument now
            instrument = who_in_fp(eachstate['simpos'])
            ccd_count = eachstate["ccd_count"]

        # Process the first AA00000000 line you see
        if pow_cmd == 'AA00000000' and firstpow:
            datestop = eachstate['datestop']
            tstop = eachstate['tstop']

            # now calculate the exposure time
            if xtztime is not None:

                # Having found the startScience and stopScience, you have an
                # OBSID interval. Now form the element and append it to
                # the Master List. We add the text version of who is in
                # the focal plane

                obsid_dict = {"datestart": datestart,
                              "datestop": datestop,
                              "tstart": tstart,
                              "tstop": tstop,
                              "ccds": ccds,
                              "start_science": xtztime,
                              "obsid": eachstate['obsid'],
                              "instrument": instrument,
                              "ccd_count": ccd_count}
                obsid_interval_list.append(obsid_dict)

            # now clear out the data values
            firstpow = False
            xtztime = None

    # End of LOOP for eachstate in cmd_states:

    # sort based on obsid
    obsid_interval_list.sort(key=lambda x: x["obsid"])
    # Now we add the stuff we get from ocat_data
    obsids = [e["obsid"] for e in obsid_interval_list]
    ocat_data = fetch_ocat_data(obsids)
    # For a vehicle load, or if the connection to the ocat server
    # fails (rare), we will get no data from the ocat so we only
    # add this info if we need to. In the case of a failed connection
    # to the OCAT server, -109 C checks should be done by hand
    if ocat_data is not None:
        ocat_keys = list(ocat_data.keys())
        ocat_keys.remove("obsid")
        for i, obsid in enumerate(obsids):
            # The obscat doesn't have info for cold ECS observations
            if obsid > 60000:
                continue
            for key in ocat_keys:
                obsid_interval_list[i][key] = ocat_data[key][i]

    # re-sort based on tstart
    obsid_interval_list.sort(key=lambda x: x["tstart"])
    return obsid_interval_list


def hrc_science_obs_filter(obsid_interval_list):
    """
    This method will filter *OUT* any HRC science observations from the
    input obsid interval list. Filtered are obs that have either
    HRC-I" or HRC-S" as the science instrument, AND an obsid LESS THAN
    50,000
    """
    acis_and_ecs_only = []
    for eachobservation in obsid_interval_list:
        if eachobservation["instrument"].startswith("ACIS-") or \
                eachobservation["obsid"] >= 60000:
            acis_and_ecs_only.append(eachobservation)
    return acis_and_ecs_only


def acis_filter(obsid_interval_list):
    """
    This method will filter between the different types of 
    ACIS observations: ACIS-I, ACIS-S, "hot" ACIS-S, and 
    cold science-orbit ECS.
    """
    acis_hot = []
    acis_s = []
    acis_i = []
    cold_ecs = []

    mylog.debug("OBSID\tCNT_RATE\tAPP_EXP\tNUM_CTS\tGRATING\tCCDS")
    for eachobs in obsid_interval_list:
        # First we check that we got ocat data using "grating"
        if "grating" in eachobs:
            eachobs["num_counts"] = int(eachobs["cnt_rate"] * eachobs["app_exp"])
            # First check to see if this is an S3 observation
            mylog.debug(f"{eachobs['obsid']}\t{eachobs['cnt_rate']}\t"
                        f"{eachobs['app_exp']*1.0e-3}\t{eachobs['num_counts']}\t"
                        f"{eachobs['grating']}\t{eachobs['ccds']}")
            if eachobs["ccd_count"] <= 2:
                # S3 with low counts
                low_ct_s3 = eachobs["num_counts"] < 300 and "S3" in eachobs["ccds"]
                # Is there another chip on? Make sure it's not S1
                if eachobs["ccd_count"] == 2:
                    low_ct_s3 &= "S1" not in eachobs["ccds"]
            else:
                # All higher ccd counts are invalid
                low_ct_s3 = False
            # Also check grating status
            hot_acis = (eachobs["grating"] == "HETG") or low_ct_s3
        else:
            hot_acis = False
        if hot_acis:
            acis_hot.append(eachobs)
        else:
            if eachobs["instrument"] == "ACIS-S":
                acis_s.append(eachobs)
            elif eachobs["instrument"] == "ACIS-I":
                acis_i.append(eachobs)
            elif eachobs["instrument"] == "HRC-S" and eachobs["obsid"] >= 60000:
                cold_ecs.append(eachobs)
            else:
                raise RuntimeError(f"Cannot determine what kind of thermal "
                                   f"limit {eachobs['obsid']} should have!")
    return acis_i, acis_s, acis_hot, cold_ecs

