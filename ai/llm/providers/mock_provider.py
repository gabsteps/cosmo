import asyncio

class MockLLMProvider:

    async def generate(self, messages):
        await asyncio.sleep(45)
        return "Resposta atrasada."


llm_provider = MockLLMProvider()

