        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-01", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d") 
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-01", "%Y-%m-%d")),
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            None,
            datetime.strptime("2019-01-07", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-01-07", "%Y-%m-%d")),
            datetime.strptime("2019-01-14", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-01", "%Y-%m-%d")),
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-13", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-19", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-19", "%Y-%m-%d")),
            datetime.strptime("2019-12-19", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-13", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-13", "%Y-%m-%d")),
            datetime.strptime("2020-01-13", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-19", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            datetime.strptime("2019-12-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            datetime.strptime("2020-02-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.2, tol_neg_mos=20.9, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-07", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.2, tol_neg_mos=20.9, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-05-23", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.2, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            datetime.strptime("2019-12-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.2, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-07", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=20.9, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            datetime.strptime("2020-02-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=20.9, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-05-23", "%Y-%m-%d")),
            datetime.strptime("2020-01-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=30, due_months_unit='D', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-03-14", "%Y-%m-%d")),
            datetime.strptime("2020-04-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-02-19", "%Y-%m-%d")),
            datetime.strptime("2020-04-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-02-19", "%Y-%m-%d")),
            datetime.strptime("2020-03-20", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-03-14", "%Y-%m-%d")),
            datetime.strptime("2020-04-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-02-19", "%Y-%m-%d")),
            datetime.strptime("2020-04-01", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-03-14", "%Y-%m-%d")),
            datetime.strptime("2020-04-13", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12.25, tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-08", "%Y-%m-%d")),
            datetime.strptime("2021-01-26", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_pos_mos=12.25, tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-21", "%Y-%m-%d")),
            datetime.strptime("2021-01-26", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_pos_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-21", "%Y-%m-%d")),
            datetime.strptime("2021-01-26", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_pos_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-08", "%Y-%m-%d")),
            datetime.strptime("2021-01-04", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-21", "%Y-%m-%d")),
            datetime.strptime("2021-02-17", "%Y-%m-%d")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D', tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-08", "%Y-%m-%d")),
            datetime.strptime("2021-01-26", "%Y-%m-%d")
        ),
