import os
import sys

from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

CHUNK_SIZE = 1_000_000
START = -2_147_483_648
END = 2_147_483_647
OUTPUT_DIR = "is_even/chunks"
ENTRYPOINT = "is_even/is_even.py"

def generate_chunk_file(chunk_id, start, end, next_chunk):
    filename = f'{OUTPUT_DIR}/chunk_{chunk_id}.py'

    with open(filename, 'w') as file:
        # Import statement
        if next_chunk is not None:
            file.write(f'from .chunk_{next_chunk} import is_even_chunk as next_chunk\n\n')

        # Create the function
        file.write("def is_even_chunk(num):\n")

        # Create this chunks numbers to check
        for i in range(start, end + 1):
            result = "True" if i % 2 == 0 else "False"

            file.write(f'    # Check if num is {i}, return {result} if it is\n')
            file.write(f'    if num == {i}: return {result}\n\n')
        
        if next_chunk is not None:
            file.write(f'    return next_chunk(num)')
        else:
            file.write(f'    return {"True" if result == 'False' else "False"}')

def generate_entrypoint():
    with open(ENTRYPOINT, 'w') as file:
        file.write('import sys\n\n')
        file.write('from chunks.chunk_0 import is_even_chunk\n\n')
        file.write('def is_even(num):\n')
        file.write('    return is_even_chunk(num)\n\n')
        file.write('if __name__ == "__main__":\n')
        file.write('    if len(sys.argv) == 2:\n')
        file.write('        print(is_even_chunk(int(sys.argv[1])))\n')
        file.write('    else:\n')
        file.write('        print("Usage: \\\"python is_even.py <number>\\\"")')

def main(min_val=START, max_val=END):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_numbers = max_val - min_val + 1
    num_chunks = (total_numbers + CHUNK_SIZE - 1) // CHUNK_SIZE

    def task(chunk_id):
        chunk_start = min_val + chunk_id * CHUNK_SIZE
        chunk_end = min(chunk_start + CHUNK_SIZE - 1, max_val)

        next_chunk = chunk_id + 1 if chunk_id + 1 < num_chunks else None

        generate_chunk_file(chunk_id, chunk_start, chunk_end, next_chunk)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(task, chunk_id) for chunk_id in range(num_chunks)]

        with tqdm(desc='Generating Chunks ', total=num_chunks, unit=' Chunk') as pbar:
            for _ in as_completed(futures):
                pbar.update(1)

    generate_entrypoint()
    print("He is the monster you've created")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(int(sys.argv[1]), int(sys.argv[2]))
    else:
        main()
