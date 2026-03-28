from src.execution.broker_shadow import ShadowBroker


def test_shadow_broker_default_mode_keeps_fill_list_empty():
    broker = ShadowBroker()

    response = broker.place_order({"symbol": "600000.SH", "quantity": 100, "price": 10.5})

    assert response == {"result": "shadow_accepted", "shadow_order_id": "shadow-0001"}
    assert broker.query_orders() == [{"symbol": "600000.SH", "quantity": 100, "price": 10.5}]
    assert broker.query_fills() == []


def test_shadow_broker_auto_fill_mode_generates_stable_fill_records():
    broker = ShadowBroker(auto_fill=True, config={"filled_at": "2026-03-28 09:35:00"})

    response_one = broker.place_order({"symbol": "600000.SH", "quantity": 100, "price": 10.5})
    response_two = broker.place_order({"symbol": "601398.SH", "qty": 200, "limit_price": 6.2})

    assert response_one == {
        "result": "shadow_accepted",
        "shadow_order_id": "shadow-0001",
        "shadow_fill_id": "shadow-0001-F001",
    }
    assert response_two == {
        "result": "shadow_accepted",
        "shadow_order_id": "shadow-0002",
        "shadow_fill_id": "shadow-0002-F001",
    }
    assert broker.query_fills() == [
        {
            "fill_id": "shadow-0001-F001",
            "order_id": "shadow-0001",
            "symbol": "600000.SH",
            "quantity": 100,
            "price": 10.5,
            "filled_at": "2026-03-28 09:35:00",
        },
        {
            "fill_id": "shadow-0002-F001",
            "order_id": "shadow-0002",
            "symbol": "601398.SH",
            "quantity": 200,
            "price": 6.2,
            "filled_at": "2026-03-28 09:35:00",
        },
    ]


def test_shadow_broker_auto_fill_uses_client_order_id_when_provided():
    broker = ShadowBroker(auto_fill=True, config={"filled_at": "2026-03-28 09:35:00"})

    response = broker.place_order(
        {
            "symbol": "600000.SH",
            "quantity": 100,
            "price": 10.5,
            "client_order_id": "run-1-O001",
        }
    )

    assert response == {
        "result": "shadow_accepted",
        "shadow_order_id": "shadow-0001",
        "shadow_fill_id": "run-1-O001-F001",
    }
    assert broker.query_fills() == [
        {
            "fill_id": "run-1-O001-F001",
            "order_id": "run-1-O001",
            "symbol": "600000.SH",
            "quantity": 100,
            "price": 10.5,
            "filled_at": "2026-03-28 09:35:00",
        }
    ]
