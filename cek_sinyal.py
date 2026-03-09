import yfinance as yf
import pandas as pd

def trading_signal_logic(ticker):
    # Ambil data 2 tahun untuk akurasi MA 200
    df = yf.download(ticker, period="2y", interval="1d")
    if df.empty: return "Data tidak ditemukan."

    # Kalkulasi Indikator
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Vol_Avg_20'] = df['Volume'].rolling(window=20).mean()

    # Logika Candlestick (Hammer & Bullish Engulfing)
    df['body'] = abs(df['Close'] - df['Open'])
    df['lower_shadow'] = df[['Close', 'Open']].min(axis=1) - df['Low']
    df['is_bullish'] = (df['Close'] > df['Open'])
    
    # Ambil data hari ini (index -1) dan kemarin (index -2)
    now = df.iloc[-1]
    prev = df.iloc[-2]

    print(f"\n=== STRATEGI SINYAL: {ticker} ===")
    print(f"Harga: {now['Close']:.0f} | MA20: {now['MA20']:.0f} | MA200: {now['MA200']:.0f}")
    print("-" * 40)

    # --- LOGIKA SINYAL MASUK (BUY) ---
    # Syarat: Harga di atas MA200 (Uptrend) + Pantulan di MA20/MA50 + Volume Tinggi
    is_hammer = (now['lower_shadow'] > (2 * now['body']))
    is_engulfing = (now['Close'] > prev['Open']) and (now['Open'] < prev['Close']) and (prev['Close'] < prev['Open'])
    
    buy_signal = False
    if now['Close'] > now['MA200']: # Hanya buy saat uptrend besar
        if (is_hammer or is_engulfing) and (now['Volume'] > now['Vol_Avg_20']):
            if now['Low'] <= now['MA20'] * 1.01: # Dekat atau menyentuh MA20
                print(">>> SINYAL: [BUY / MASUK]")
                print("Alasan: Pola Bullish terdeteksi di area Support MA20 dengan Volume kuat.")
                buy_signal = True

    # --- LOGIKA SINYAL KELUAR (SELL / TAKE PROFIT) ---
    # Syarat: Harga memotong MA20 ke bawah (Patah Tren) atau MA20 Cross MA50 ke bawah
    sell_signal = False
    if now['Close'] < now['MA20']:
        print(">>> SINYAL: [SELL / KELUAR - STOP LOSS/TAKE PROFIT]")
        print("Alasan: Harga ditutup di bawah MA20 (Tren jangka pendek patah).")
        sell_signal = True
    elif now['MA20'] < now['MA50'] and prev['MA20'] >= prev['MA50']:
        print(">>> SINYAL: [SELL / KELUAR - DEAD CROSS]")
        print("Alasan: MA20 memotong ke bawah MA50.")
        sell_signal = True

    if not buy_signal and not sell_signal:
        print("STATUS: WAIT & SEE (Belum ada sinyal kuat)")

# Jalankan contoh
trading_signal_logic("ASII.JK")
