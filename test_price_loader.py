from src.loader.price_loader import load_price

price = load_price(
    "005930",
    "2025-01-01",
    "2025-01-31"
)

print(price.head())
print(price.shape)