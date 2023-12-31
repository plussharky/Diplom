from keras.models import Sequential
from keras.layers import Dense, Conv1D, MaxPooling1D, Flatten, Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def truncate_text(texts, max_length):
    truncated_text = []
    for text in texts:
        if len(text) > max_length:
            truncated_text.append(text[:max_length])
        else:
            truncated_text.append(text)
    return truncated_text


def count_unique_words_in_texts(texts):
    unique_words = set()
    for text in texts:
        words = text.split()
        unique_words.update(words)
    unique_words_count = len(unique_words)
    return unique_words_count

def count_words_in_texts(texts):
    words_count = 0
    for text in texts:
        words_count = words_count + len(text.split())

    return words_count

def count_max_len_in_texts(texts):
    max_len = 0
    for text in texts:
        text_len = len(text.split())
        if text_len > max_len:
            max_len = text_len

    return max_len

def clean_array(arr):
    # Удаление значений None и NaN
    cleaned = [str(x) for x in arr if x is not None and str(x).lower() != 'nan']
    return cleaned

def batch_generator(texts, labels, batch_size):
    # Создание бесконечного цикла, чтобы генератор продолжал возвращать данные
    while True:
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_labels = labels[i:i+batch_size]
            data = tokenizer.texts_to_sequences(batch_texts)
            data_pad = pad_sequences(data, maxlen=max_len)
            yield data_pad, np.array(batch_labels)

def new_batch_generator(texts, labels, batch_size):
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_labels = labels[i:i+batch_size]
        data = tokenizer.texts_to_sequences(batch_texts)
        data_pad = pad_sequences(data, maxlen=max_len)
        yield data_pad, np.array(batch_labels)

# Загрузка данных из CSV-файла
legitime_texts = pd.read_csv('texts.csv', sep='\t', encoding='utf-16', dtype=str)
phishing_texts = pd.read_csv('phishing_texts.csv', sep='\t', encoding='utf-16', dtype=str)
print('текста загружены')
# Извлечение колонки 'text' в массив
legitime_texts_array = legitime_texts['text'].values.tolist()
phishing_texts_array = phishing_texts['text'].values.tolist()
print('текста получены')
# Очистка массива
legitime_texts_array = clean_array(legitime_texts_array)
phishing_texts_array = clean_array(phishing_texts_array)
print('текста очищены')
# Обрезка текста
avg_words_in_legitime_count = count_words_in_texts(legitime_texts_array) // len(legitime_texts_array)
avg_words_in_phishing_count = count_words_in_texts(phishing_texts_array) // len(phishing_texts_array)

#avg_words = (avg_words_in_legitime_count + avg_words_in_phishing_count) // 2
avg_words = max(avg_words_in_legitime_count, avg_words_in_phishing_count)

legitime_texts_array = truncate_text(legitime_texts_array, avg_words)
phishing_texts_array = truncate_text(phishing_texts_array, avg_words)

# предположим, что у нас есть некоторые данные
texts = legitime_texts_array + phishing_texts_array
legitime_count = len(legitime_texts_array)
phishing_count = len(phishing_texts_array)

legitime_labels = [1] * legitime_count
phishing_labels = [0] * phishing_count
labels = legitime_labels + phishing_labels

words_count = count_unique_words_in_texts(texts)
max_len = count_max_len_in_texts(texts)
avg_words_count = count_words_in_texts(texts) // len(texts)

print('текста посчитаны')
tokenizer = Tokenizer(num_words=words_count,
    filters='!–"—#$%&amp;()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r«»',
    lower=True,
    split=' ',
    char_level=False)
tokenizer.fit_on_texts(texts)
print('токенайзер посчитан')

#data = tokenizer.texts_to_sequences(texts)
#data_pad = pad_sequences(data, maxlen=max_len)

batch_size = 100  # Выберите размер батча, который подходит для вашей системы
steps_per_epoch = len(texts) // batch_size  # Количество шагов на эпоху
train_generator = batch_generator(texts, labels, batch_size)
print('генератор посчитан')

# создание модели
model = Sequential()
model.add(Embedding(words_count, 128, input_length=max_len))
model.add(Conv1D(128, 5, activation='relu'))
model.add(MaxPooling1D(5))
model.add(Flatten())
model.add(Dense(1, activation='sigmoid'))

# компиляция и обучение модели
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(train_generator, steps_per_epoch=steps_per_epoch, epochs=20)
#history = model.fit(train_generator, steps_per_epoch=steps_per_epoch, epochs=20, validation_split=0.2)

model.save_weights('text_weights.h5') #Сохранение весов модели
model.save('text_model.keras') #Сохранение модели