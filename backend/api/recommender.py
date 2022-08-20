from http import HTTPStatus
from typing import Dict

from bson import ObjectId
from fastapi import APIRouter, Request

from backend.utils.helper import construct_response
from common import config, database
from common.config import logger
from common.utils import send_request

router = APIRouter()


@router.get("/predict")
@construct_response
def predict(request: Request, uid: str, limit: int) -> Dict:
    """Call the Recommender Engine to get user movie recommendations

    Args:
        request (Request): API Request
        uid (str): User ID
        limit (int): Recommendation limit

    Returns:
        Dict: Movie recommendations data
    """
    # Get user historical movies from database
    search_dict = {"uid": ObjectId(uid)}
    documents = database.db_get_documents("user", search_dict)
    if documents:
        user = documents[0]
        payload = {"user_movies": user.get("selected_movies", [])}
    else:
        payload = {"user_movies": []}

    # Get movie recommendations from Recommender API
    status_code, movie_recommendations = send_request(
        config.RECOMMENDER_ENGINE_URL, "recommend", "POST", payload=payload
    )
    if status_code == HTTPStatus.OK:
        predicted_movies = movie_recommendations.get("predicted_movies", [])

        # Limit the predicted movies list
        if limit and len(predicted_movies) > limit:
            predicted_movies = predicted_movies[:limit]

        response = {"data": predicted_movies, "status_code": HTTPStatus.OK}
    else:
        logger.warning(f"Received status: {status_code} from Recommender Engine")
        response = {"data": [], "status_code": HTTPStatus.OK}

    return response
