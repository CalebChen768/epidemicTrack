from db import DBService

if __name__ == '__main__':
    db_service = DBService()
    # test cpt
    # cpt1 = db_service.create_checkpoint()
    # cpk2 = db_service.create_checkpoint()
    # cpk3 = db_service.create_checkpoint()
    # cpk4 = db_service.create_checkpoint()
    # cpk5 = db_service.create_checkpoint()

    # # # test add_an_edge
    # db_service.add_an_edge(cpt1, 1, cpk2, 2)
    # db_service.add_an_edge(cpt1, 1, cpk5, 2)
    # db_service.add_an_edge(cpt1, 1, cpk3, 3)
    # db_service.add_an_edge(cpk2, 2, cpk4, 4)
    # db_service.add_an_edge(cpk3, 3, cpk4, 4)
    # db_service.add_an_edge(cpk5, 2, cpt1, 5)
    # db_service.add_an_edge(cpk5, 2, cpk2, 5)
    # db_service.add_an_edge(cpk4, 4, cpt1, 6)
    # db_service.add_an_edge(cpk2, 5, cpk4, 6)

    # # test set_risk
    # db_service.set_risk([{"checkpoint_id": cpt1, "time": 1}, {"checkpoint_id": cpk2, "time": 5}])

    visited_places = [
        # {"checkpoint_id": "LM+EsCBTS3", "time": 1},  # high
        # {"checkpoint_id": "4fzSij2rRB", "time": 4},  # medium
        # {"checkpoint_id": "DYFYZlbmRZ", "time": 3},   # medium
        {"checkpoint_id": "zZ4i2BORTB", "time": 7},  # none
    ]
    print(db_service.get_risk_level(visited_places))
