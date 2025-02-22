from db import DBService

if __name__ == '__main__':
    db_service = DBService()
    # test cpt
    # cpt1 = db_service.create_checkpoint()
    # cpk2 = db_service.create_checkpoint()
    # cpk3 = db_service.create_checkpoint()
    # cpk4 = db_service.create_checkpoint()

    # # test add_an_edge
    # db_service.add_an_edge(cpt1, 1, cpk2, 2)
    # db_service.add_an_edge(cpt1, 1, cpk3, 3)
    # db_service.add_an_edge(cpk2, 2, cpk4, 4)
    # db_service.add_an_edge(cpk3, 3, cpk4, 4)
    # db_service.add_an_edge(cpk4, 4, cpt1, 1)

    # test set_risk
    print(db_service.set_risk([{"checkpoint_id": "EaxWEYXgTT", "time": 1}], "medium"))