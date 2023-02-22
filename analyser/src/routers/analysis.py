from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from ..analysis import AnalysisAPI, analysis_api_dep
from .. import models

router = APIRouter()

@router.post('/perform-portfolio-analysis')
async def perform_the_theoretical_analysis_for_a_portfolio_of_holdings(
    inputs: models.PerformAnalysisInputs,
    analysis_api: AnalysisAPI = Depends(analysis_api_dep)
):
    try:
        await analysis_api.perform_portfolio_analysis(inputs)
        return JSONResponse(status_code=200, content={
            "message": "Portfolio analysis scheduled successfully",
            "ok": True,
        })
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "message": "The server failed to process the request",
            "error": str(e),
        })


@router.post('/get-portfolio-analysis')
async def retrieve_the_theoretical_analysis_for_a_portfolio_of_holdings(
    inputs: models.GetAnalysisInputs,
    analysis_api: AnalysisAPI = Depends(analysis_api_dep)
):
    try:
        return await analysis_api.return_portfolio_analysis(inputs)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "message": "The server failed to process the request",
            "error": str(e),
        })


@router.post('/publish-analysis-result')
async def publish_the_result_of_the_theoretical_portfolio_analysis_for_a_portfolio_of_holdings(
    inputs: models.AnalysisResult,
    analysis_api: AnalysisAPI = Depends(analysis_api_dep),
):
    try:
        return await analysis_api.write_results_to_mongo(inputs)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "message": "The server failed to process the request",
            "error": str(e),
        })