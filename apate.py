import argparse
import sys
import io
import os
import struct

MASK_LENGTH_INDICATOR_LENGTH = 4
JPG_HEAD = bytes([0xff, 0xd8, 0xff, 0xe1])
MOV_HEAD = bytes([0x6d, 0x6f, 0x6f, 0x76])
MP4_HEAD = bytes([
    0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70, 0x69,
    0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00, 0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32, 0x61,
    0x76, 0x63, 0x31, 0x6D, 0x70, 0x34, 0x31
])

EXE_HEAD = [
    0x4D, 0x5A, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00, 0x04,
    0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0xB8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x0E, 0x1F, 0xBA, 0x0E, 0x00, 0xB4, 0x09, 0xCD, 0x21,
    0xB8, 0x01, 0x4C, 0xCD, 0x21, 0x54, 0x68, 0x69, 0x73, 0x20, 0x70, 0x72, 0x6F, 0x67, 0x72, 0x61,
    0x6D, 0x20, 0x63, 0x61, 0x6E, 0x6E, 0x6F, 0x74, 0x20, 0x62, 0x65, 0x20, 0x72, 0x75, 0x6E, 0x20,
    0x69, 0x6E, 0x20, 0x44, 0x4F, 0x53, 0x20, 0x6D, 0x6F, 0x64, 0x65, 0x2E, 0x0D, 0x0D, 0x0A, 0x24,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]


def int_to_bytes(value):
    return struct.pack('<I', value)


def reveal(file_path):
    try:
        file_length = os.path.getsize(file_path)
        with open(file_path, 'r+b') as f:
            f.seek(file_length - MASK_LENGTH_INDICATOR_LENGTH)
            mask_head_length = bytes_to_int(f.read(MASK_LENGTH_INDICATOR_LENGTH))
            if mask_head_length <= (file_length - MASK_LENGTH_INDICATOR_LENGTH - mask_head_length):
                f.seek(file_length - MASK_LENGTH_INDICATOR_LENGTH - mask_head_length)
                original_head = f.read(mask_head_length)
            else:
                f.seek(mask_head_length)
                original_head = f.read(file_length - MASK_LENGTH_INDICATOR_LENGTH - mask_head_length)
            f.seek(0)
            f.write(reverse_byte_array(original_head))
            f.truncate(file_length - mask_head_length - MASK_LENGTH_INDICATOR_LENGTH)

            directory, filename = os.path.split(file_path)
            name_parts = filename.split('.')
            file_name_len = len(name_parts)
            if file_name_len > 1:
                new_path = os.path.join(directory, filename.replace('.' + name_parts[file_name_len - 1], ''))
                os.rename(file_path, new_path)
            print(f"转换成功:{file_path}")
        return True
    except Exception as e:
        print(f"转换失败{file_path}: {e}")
        return False


def disguise(file_path, mask_head=MOV_HEAD):
    try:
        with open(file_path, 'r+b') as f:
            extension = 'mp4'
            if mask_head == JPG_HEAD:
                extension = 'jpg'
            elif mask_head == EXE_HEAD:
                extension = 'exe'
            file_length = os.path.getsize(file_path)
            original_head = f.read(len(mask_head)) if file_length >= len(mask_head) else f.read(file_length)
            f.seek(0)
            f.write(mask_head)
            f.seek(0, os.SEEK_END)
            f.write(reverse_byte_array(original_head))
            f.write(int_to_bytes(len(mask_head)))
            directory, filename = os.path.split(file_path)
            new_path = os.path.join(directory, filename + '.' + extension)
            os.rename(file_path, new_path)
            print(f"伪装成功:{file_path}")
        return True
    except Exception as e:
        print(f"伪装失败{file_path}: {e}")
        return False


def reverse_byte_array(buffer):
    return buffer[::-1]


def bytes_to_int(byte_array):
    return struct.unpack('<I', byte_array)[0]


def rename_file(filepath, target_extension, reveal_extension):
    if filepath.endswith(target_extension + reveal_extension):
        new_filepath = filepath.replace(reveal_extension, '')
        os.rename(filepath, new_filepath)


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()


if __name__ == '__main__':
    parser = CustomArgumentParser(description="对文件进行格式伪装和去伪装的工具")
    parser.add_argument('-p', '--path', type=str, required=True, help='文件路径')
    parser.add_argument('-d', '--disguise', action='store_true', required=False, help='文件伪装')
    parser.add_argument('-r', '--reveal', action='store_true', required=False, help='文件去伪装')

    stderr_backup = sys.stderr
    sys.stderr = io.StringIO()

    args = parser.parse_args()
    if (not args.reveal) and (not args.disguise):
        print("请选择文件要处理方式: -r 去伪装 或者 -d 伪装")
        sys.exit(1)
    if args.reveal and args.disguise:
        print("请选择文件要处理方式: -r 去伪装 或者 -d 伪装")
        sys.exit(1)
    file_path = args.path
    if not os.path.exists(file_path):
        print(f"{file_path} 不存在")
        sys.exit(1)
    if os.path.isdir(file_path):
        for file_name in os.listdir(file_path):
            path = os.path.join(file_path, file_name)
            if args.reveal:
                reveal(path)
            if args.disguise:
                disguise(path)
        sys.exit(0)
    if args.reveal:
        reveal(file_path)
    if args.disguise:
        disguise(file_path)
