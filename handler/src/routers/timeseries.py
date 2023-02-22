from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from ..timeseries import TimeseriesAPI, timeseries_api_dep
from .. import models

router = APIRouter()

@router.post('/portfolio-timeseries')
async def retrieve_the_historical_timeseries_data_for_a_portfolio_of_holdings(
    inputs: models.TimeseriesInputs,
    timeseries_api: TimeseriesAPI = Depends(timeseries_api_dep)
):
    try:
        return await timeseries_api.return_portfolio_timeseries_data(inputs)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "message": "The server failed to process the request",
            "error": str(e),
        })


@router.post('/publish-timeseries-result')
async def publish_the_result_of_the_timeseries_analysis_for_a_portfolio_of_holdings(
    inputs: models.TimeseriesResult,
    timeseries_api: TimeseriesAPI = Depends(timeseries_api_dep),
):
    try:
        return await timeseries_api.write_results_to_cache(inputs)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "message": "The server failed to process the request",
            "error": str(e),
        })

# @router.post('/portfolio-analysis')
# def retrieve_the_historical_timeseries_data_for_a_portfolio_of_holdings(
#     inputs: TimeseriesInputs,
#     connections: Connections = Depends(connections_dep)
# ):
#     timeseries_api = TimeseriesAPI(connections.redis, connections.nats)
#     try:
#         return timeseries_api.calculate_portfolio_analysis(inputs.holdings, inputs.range)
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="The server failed to process the request")