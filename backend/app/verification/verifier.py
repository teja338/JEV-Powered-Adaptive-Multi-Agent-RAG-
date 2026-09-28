from backend.app.verification.rag_verifier import rag_verifier
from backend.app.verification.web_verifier import web_verifier
from backend.app.verification.code_verifier import code_verifier

class VerifierFactory:
    @staticmethod
    def get_verifier(agent_type: str):
        if agent_type == "rag":
            return rag_verifier
        elif agent_type == "web":
            return web_verifier
        elif agent_type == "code":
            return code_verifier
        raise ValueError(f"Unknown agent type: {agent_type}")
