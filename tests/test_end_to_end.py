import pytest

from collect_produce.src.service import (
    collect_produce_service_run,
    AIVEN_KAFKA_PRODUCER,
    TOPIC,
    TARGET_PATTERN,
    TARGET_URL
)
from consume_publish.src.service import (
    consume_publish_run,
    DATABASE,
    AIVEN_KAFKA_CONSUMER,
)


INVALID_URL = 'https://monedo.jpy'


TEST_DATA = [
    {
        'query': f"SELECT COUNT(*) FROM {DATABASE.TABLE} WHERE url='{TARGET_URL}' AND content_validation=true",
        'url': TARGET_URL,
        'pattern': TARGET_PATTERN,
        'cycles': 1
    },
    {
        'query': f"SELECT COUNT(*) FROM {DATABASE.TABLE} WHERE url='{TARGET_URL}' AND content_validation=false",
        'url': TARGET_URL,
        'pattern': 'some invalid content 8939-',
        'cycles': 2
    },
    {
        'query': f"SELECT COUNT(*) FROM {DATABASE.TABLE} WHERE url='{TARGET_URL}' AND content_validation is NULL",
        'url': TARGET_URL,
        'pattern': None,
        'cycles': 1
    },
    {
        'query': f"SELECT COUNT(*) FROM {DATABASE.TABLE} WHERE url='{INVALID_URL}'",
        'url': INVALID_URL,
        'pattern': None,
        'cycles': 1
    }
]


@pytest.mark.end_to_end
@pytest.mark.slow
@pytest.mark.parametrize('test_input', TEST_DATA)
def test_e2e_metric_works(test_input):
    # This test could produce false negative result if other sample
    # of services is running. In future it's important to post to a separate topic
    count = DATABASE.execute_sql(test_input['query'])[0][0]
    collect_produce_service_run(
        test_input['url'],
        AIVEN_KAFKA_PRODUCER,
        TOPIC,
        sleep_time=1,
        pattern=test_input['pattern'],
        cycles=test_input['cycles']
    )
    latest_count = DATABASE.execute_sql(test_input['query'])[0][0]
    msg = f'Number of DB entries changed from {count} to {latest_count} during execution'
    msg = f'{msg} of web metric collection. Please make sure no other services post'
    msg = f'{msg} web metrics to the same topic!. Query: {test_input["query"]}'
    assert count == latest_count, msg
    consume_publish_run(AIVEN_KAFKA_CONSUMER, DATABASE, sleep_time=1, cycles=test_input['cycles'])
    latest_count = DATABASE.execute_sql(test_input['query'])[0][0]
    msg = f'Number of DB entries have not changed from {count} to {latest_count}'
    msg = f'{msg} during execution. Expected to have at least {test_input["cycles"]} entry more'
    assert latest_count >= count + test_input['cycles'], msg
