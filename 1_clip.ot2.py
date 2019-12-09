from opentrons import labware, instruments, modules, robot


clips_dict={"prefixes_wells": ["A8", "A7", "C5", "C8", "C11", "A7", "A7", "A7", "A7", "A7", "A7", "A7"], "prefixes_plates": ["2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2"], "suffixes_wells": ["B7", "C1", "C2", "C3", "B8", "C1", "C1", "C1", "C1", "C1", "C1", "B8"], "suffixes_plates": ["2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2"], "parts_wells": ["E1", "G1", "C2", "B2", "D2", "H1", "F2", "G2", "H2", "A3", "B3", "C2"], "parts_plates": ["5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"], "parts_vols": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "water_vols": [7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0]}


def clip(
        prefixes_wells,
        prefixes_plates,
        suffixes_wells,
        suffixes_plates,
        parts_wells,
        parts_plates,
        parts_vols,
        water_vols,
        tiprack_type="tiprack-10ul"):
    """Implements linker ligation reactions using an opentrons OT-2."""

    # Constants
    INITIAL_TIP = 'A1'
    CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9']
    PIPETTE_TYPE = 'P10_Single'
    PIPETTE_MOUNT = 'left'
    SOURCE_PLATE_TYPE = '4ti-0960_FrameStar'
    DESTINATION_PLATE_TYPE = '4ti-0960_FrameStar'
    DESTINATION_PLATE_POSITION = '1'
    TUBE_RACK_TYPE = 'tube-rack_E1415-1500'
    TUBE_RACK_POSITION = '4'
    MASTER_MIX_WELL = 'A1'
    WATER_WELL = 'A2'
    INITIAL_DESTINATION_WELL = 'A1'
    MASTER_MIX_VOLUME = 20
    LINKER_MIX_SETTINGS = (1, 3)
    PART_MIX_SETTINGS = (4, 5)

    # Tiprack slots
    total_tips = 4 * len(parts_wells)
    letter_dict = {'A': 0, 'B': 1, 'C': 2,
                   'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    tiprack_1_tips = (
        13 - int(INITIAL_TIP[1:])) * 8 - letter_dict[INITIAL_TIP[0]]
    if total_tips > tiprack_1_tips:
        tiprack_num = 1 + (total_tips - tiprack_1_tips) // 96 + \
            (1 if (total_tips - tiprack_1_tips) % 96 > 0 else 0)
    else:
        tiprack_num = 1
    slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]

    # Define source plates
    source_plates = {}
    source_plates_keys = list(set((prefixes_plates + suffixes_plates + parts_plates)))
    for key in source_plates_keys:
        source_plates[key] = labware.load(SOURCE_PLATE_TYPE, key)

    # Define remaining labware
    tipracks = [labware.load(tiprack_type, slot) for slot in slots]
    if PIPETTE_TYPE != 'P10_Single':
        print('Define labware must be changed to use', PIPETTE_TYPE)
        exit()
    p10 = instruments.P10_Single(mount=PIPETTE_MOUNT, tip_racks=tipracks)
    p10.start_at_tip(tipracks[0].well(INITIAL_TIP))
    destination_plate = labware.load(
        DESTINATION_PLATE_TYPE, DESTINATION_PLATE_POSITION)
    tube_rack = labware.load(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
    master_mix = tube_rack.wells(MASTER_MIX_WELL)
    water = tube_rack.wells(WATER_WELL)
    destination_wells = destination_plate.wells(
        INITIAL_DESTINATION_WELL, length=int(len(parts_wells)))
    
    tiprack300 = labware.load('opentrons_96_tiprack_300ul', slot = "8")
    p300 = instruments.P300_Single(mount = 'right', tip_racks = [tiprack300])

# Operation
       
    p10.distribute(water_vols, water, destination_wells, new_tip='never')
    
    p300.pick_up_tip()
    p300.distribute(MASTER_MIX_VOLUME, master_mix, destination_wells, new_tip='never')
    p300.drop_tip()

  
    for clip_num in range(len(parts_wells)):
        p10.transfer(1, source_plates[prefixes_plates[clip_num]].wells(prefixes_wells[clip_num]),
                         destination_wells[clip_num], mix_after=LINKER_MIX_SETTINGS)
        p10.transfer(1, source_plates[suffixes_plates[clip_num]].wells(suffixes_wells[clip_num]),
                         destination_wells[clip_num], mix_after=LINKER_MIX_SETTINGS)
        p10.transfer(parts_vols[clip_num], source_plates[parts_plates[clip_num]].wells(parts_wells[clip_num]),
                         destination_wells[clip_num], mix_after=PART_MIX_SETTINGS)


clip(**clips_dict)

# Robot comments
for c in robot.commands():
    print(c)
