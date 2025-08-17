from click.testing import CliRunner

from ticker_etl.main import main

def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ['--ticker', 'AAPL', '--trade-date-from', '2024-01-01', '--trade-date-to', '2024-01-10'])
    assert result.exit_code == 0
    # assert result.output == 'Hello Peter!\n'
