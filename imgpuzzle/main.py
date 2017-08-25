"""パズルアプリ."""
import random
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox

from PIL import ImageTk, Image


class Puzzle(ttk.Frame):
    """3*3パズル."""

    def __init__(self, master, image):
        """初期化."""
        super().__init__(master)
        self.origin_image = image
        self.setup_images(image)
        self.update_gui()

    def setup_images(self, image):
        """パズル画像の準備処理."""
        # 画像を分割したリストをself.imagesとする
        self.images = self.split_image(image, split=3)

        # そのリストを細部までシャッフル
        self.shuffle(self.images)

        # パズルなので、一つ抜く
        self.images[0][0] = 0, 0, None

    def split_image(self, image, split=3):
        """画像を3*3等に分割し、リストに格納しかえす."""
        origin_width, origin_height = image.size
        split_width = origin_width / split
        split_height = origin_height / split
        images = [[None for x in range(split)] for y in range(split)]
        for row_index in range(split):
            for col_index in range(split):
                row = row_index * split_height
                col = col_index * split_width
                box = (col, row, col + split_width, row + split_height)
                img = image.crop(box)
                img_tk = ImageTk.PhotoImage(img, master=self)
                images[row_index][col_index] = row_index, col_index, img_tk
        return images

    def shuffle(self, lst):
        """リストをシャッフルする。2次元のリストもシャッフルできる."""
        if isinstance(lst, list):
            random.shuffle(lst)
            for l in lst:
                self.shuffle(l)

    def update_gui(self):
        """パズル画面の作成."""
        # gridで貼り付けたレイアウトを解除
        for widget in self.grid_slaves():
            widget.grid_forget()

        for row_index, row in enumerate(self.images):
            for col_index, data in enumerate(row):
                img_tk = data[2]
                if img_tk:
                    label = ttk.Label(
                        self, image=img_tk,
                        text='{0}{1}'.format(row_index, col_index)
                    )
                    label.grid(row=row_index, column=col_index)
        self.bind_all('<Button-1>', self.push)

    def check_space(self, row_index, col_index):
        """上下左右に空白エリアがあれば、空白エリアの座標を返す."""
        # 上と下に空白エリアはあるか？
        for r in [row_index - 1, row_index + 1]:
            try:
                data = self.images[r][col_index]
            except IndexError:
                continue
            else:
                if data[2] is None:
                    return r, col_index

        # 左と右に空白エリアはあるか？
        for c in [col_index - 1, col_index + 1]:
            try:
                data = self.images[row_index][c]
            except IndexError:
                continue
            else:
                if data[2] is None:
                    return row_index, c

        # 見つからなければNoneを返す
        return None

    def is_complete(self):
        """パズルが完成していればTrue."""
        for row_index, row in enumerate(self.images):
            for col_index, data in enumerate(row):
                origin_row_index, origin_col_index, img_tk = data
                if img_tk:
                    if origin_row_index != row_index or origin_col_index != col_index:
                        return False
        return True

    def finish(self):
        """終了画面の作成."""
        # gridで貼り付けたレイアウトを解除
        for widget in self.grid_slaves():
            widget.grid_forget()

        # イベントの解除
        self.unbind_all('<Button-1>')

        # 画面に元々の画像を表示する
        self.origin_image_tk = ImageTk.PhotoImage(
            self.origin_image, master=self)
        label = ttk.Label(self, image=self.origin_image_tk)
        label.grid(row=0, column=0)

        # 有り難いお言葉
        messagebox.showinfo(message='おめでとうございます、完成です')

    def push(self, event):
        """パズルを押した際に呼ばれる."""
        try:
            text = event.widget['text']
        # textがないウィジェットを押したら、TclError
        except tk.TclError:
            pass
        else:
            row_index, col_index = [int(x) for x in text]
            space = self.check_space(row_index, col_index)
            if space:
                # スペースの座標を取得
                space_row, space_col = space

                # スペース部分とクリックされたパズルを入れ替える
                clicked_data = self.images[row_index][col_index]
                space_data = self.images[space_row][space_col]
                self.images[row_index][col_index] = space_data
                self.images[space_row][space_col] = clicked_data

                # パズルが完成していれば
                if self.is_complete():
                    self.finish()
                else:
                    self.update_gui()

            # 上下左右にスペースのない部分をクリックしても、何もしない
            else:
                pass


def main():
    """実行用関数."""
    root = tk.Tk()
    root.title('パズル')
    filename = filedialog.askopenfilename()
    image = None

    # 画像を開こうと試みる
    try:
        image = Image.open(filename)

    # open()できなかった(画像以外のファイルを開いた)
    except OSError:
        messagebox.showerror(message='画像を開いてください')

    # キャンセルボタンを押した
    except AttributeError:
        pass

    # 画像ファイルをきちんと開いた
    else:
        app = Puzzle(root, image)
        app.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        root.mainloop()

    # 画像を開いていたら閉じる
    finally:
        if image:
            image.close()


if __name__ == '__main__':
    main()
