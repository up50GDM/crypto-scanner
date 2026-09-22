import os
import time
import ccxt
import pandas as pd

def fetch_historical_data(symbol, timeframe='1h', since_date='2022-01-01T00:00:00Z'):
    """
    Lädt historische OHLCV-Daten über ccxt herunter.
    Berücksichtigt das Rate-Limit der Börse durch Paginierung.
    """
    # Wir nutzen Binance, da es tiefe Historie ohne API Key erlaubt
    exchange = ccxt.binance({"enableRateLimit": True})
    
    # Konvertiere das Startdatum in einen Timestamp (Millisekunden)
    since = exchange.parse8601(since_date)
    all_ohlcv = []
    
    print(f"Starte Download für {symbol} (Intervall: {timeframe}) ab {since_date}...")
    
    while True:
        try:
            # Datenblock abrufen
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            
            # Wenn keine neuen Daten mehr zurückkommen, beenden
            if len(ohlcv) == 0:
                break
                
            all_ohlcv.extend(ohlcv)
            
            # Nächster Startpunkt ist der Timestamp der letzten Kerze + 1 Millisekunde
            since = ohlcv[-1][0] + 1
            
            print(f"   ... {len(all_ohlcv)} Kerzen geladen.")
            
            # Kurze Pause einlegen, um das Rate-Limit definitiv nicht zu verletzen
            time.sleep(exchange.rateLimit / 1000)
            
        except Exception as e:
            print(f"Fehler bei {symbol}: {e}. Warte 5 Sekunden...")
            time.sleep(5)
            
    if not all_ohlcv:
        print(f"Keine Daten für {symbol} gefunden.")
        return pd.DataFrame()

    # DataFrame erstellen
    df = pd.DataFrame(
        all_ohlcv, 
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    
    # Timestamp in lesbares Datumsformat umwandeln (Binance liefert Millisekunden)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Zur Sicherheit doppelte Einträge entfernen
    df = df.drop_duplicates(subset=['timestamp'])
    
    return df


if __name__ == "__main__":
    # Ordner 'data' erstellen, falls nicht vorhanden
    os.makedirs("data", exist_ok=True)
    
    # Binance nutzt standardmäßig USDT (Tether) als USD-Äquivalent
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    
    for sym in symbols:
        # Daten abholen
        df = fetch_historical_data(sym, timeframe='1h', since_date='2022-01-01T00:00:00Z')
        
        if not df.empty:
            # Dateinamen für unser Projekt anpassen (z.B. BTC_USD.csv)
            filename = sym.replace("/", "_").replace("USDT", "USD") + ".csv"
            filepath = os.path.join("data", filename)
            
            # Als CSV speichern
            df.to_csv(filepath, index=False)
            print(f"✅ ERFOLG: {filepath} wurde gespeichert. ({len(df)} Zeilen)\n")
