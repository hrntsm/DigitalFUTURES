# Day3

3 日目は最適化についての基礎的な内容の紹介と実際に構造最適化を行います。
最適化は Grasshopper 内での既存のツールを使ったものだけでなく、RhinoCompute と Python を使った最適化や応答曲面の作成についても紹介します。

## Grasshopper に既にあるコンポーネントでの最適化

//TODO: 堀川さんのハンズオンを見てるとそもそも Wallacei とか最適化そのものについて紹介してもよいという印象を受けた。

### Galapagos の紹介

一番簡単

### Wallacei の紹介

公式 Example の紹介するだけでもよさそう
MO でできることが特徴
結果の分析ができるので良い

### Tunny の紹介

Tunny は自分が Wallacei をつかっていて不便な個所を修正した。

- ジオメトリが保存されない
- GAが収束しない解析問題に対応したい
  - ベイズ最適化に対応した点が大きい


## RhinoCompute と Python の連携

RhinoInside や Rhino3dm、RhinoCompute など コードから Rhino のデータ、機能を扱う機能は現在色々と提供されています。
言語としては C#、Python、Javascript の 3 つが公式でライブラリが提供されており、いろんな環境で使いやすいように整備されています。

とはいえ、現実問題、普段コードを書いていない人がこういった機能をうまく使うことは難しいです。

その中で、RhinoCompute は Grasshopper から使用するコンポーネントである Hops が公式から提供されており、コードを使うことなく使用することができる機能になっています。

Hops v0.8 のアップデートで Hops で読み込んだ Grasshopper をデータを動かす Python コードを自動生成して出力する機能が追加されました。
これを使うことで Python にあまり慣れていない人でも Grasshopper を コードにように扱うことで、Python で簡単に Rhino のデータを扱うことができるようになりました。

ここではそのやり方について紹介します。

### RhinoCompute について

公式サイトで RhinoCompute について確認します

- https://developer.rhino3d.com/guides/compute/

### Hops から Python のコードを出力する

PackageManager で Hops をインストールする際には 0.8 以降のバージョンを指定するようにしてください。
最新は 0.15(2022/6/12 時点) です。

ここでは例として以下のように足し算をするコンポーネントを作成します。

![Sum Component](https://hiron.dev/article-images/grasshopper-as-a-code-with-python/SumComponent.png)

Hops で読み込んで上の画像で上げた足し算をする機能を持った Hops コンポーネントが作成します。
値をインプットしたらコンポーネントを右クリックします。
クリックすると以下のようコンテキストメニューが出てくるのでに Export から Export python sample... を選びます。

![Export python code](https://hiron.dev/article-images/grasshopper-as-a-code-with-python/ExportPythonCode.png)

例えば sum.py と名前をつけてデスクトップに出力先を選択すると今回であれば以下のようなコードが生成されます。

```python
# pip install compute_rhino3d and rhino3dm
import compute_rhino3d.Util
import compute_rhino3d.Grasshopper as gh
import rhino3dm
import json

compute_rhino3d.Util.url = 'http://localhost:6500/'

# create DataTree for each input
input_trees = []
tree = gh.DataTree("A")
tree.Append([0], ["10.0"])
input_trees.append(tree)

tree = gh.DataTree("B")
tree.Append([0], ["5.0"])
input_trees.append(tree)

output = gh.EvaluateDefinition('Path/to/Desktop/sum.gh', input_trees)
errors = output['errors']
if errors:
    print('ERRORS')
    for error in errors:
        print(error)
warnings = output['warnings']
if warnings:
    print('WARNINGS')
    for warning in warnings:
        print(warning)

values = output['values']
for value in values:
    name = value['ParamName']
    inner_tree = value['InnerTree']
    print(name)
    for path in inner_tree:
        print(path)
        values_at_path = inner_tree[path]
        for value_at_path in values_at_path:
            data = value_at_path['data']
            if isinstance(data, str) and 'archive3dm' in data:
                obj = rhino3dm.CommonObject.Decode(json.loads(data))
                print(obj)
            else:
                print(data)
```

### Python で Grasshopper を動かしてみる

では出力されたコードを確認していきましょう。
まず環境に Python がインストールされている必要があります。
もしインストールされていない方は、以下からインストールしてください。

- https://www.python.org/downloads/

なお私の環境では Python 3.9 を使用しています。

#### 環境の構築

上記で生成されたコードを見ると最初の行に以下のように書かれています。

```python
# pip install compute_rhino3d and rhino3dm
import compute_rhino3d.Util
import compute_rhino3d.Grasshopper as gh
import rhino3dm
import json
```

冒頭にあるように pip を使って必要なライブラリをインストールします。
pip とは Python のパッケージマネージャーになります。
あまりパッケージマネージャーになじみのない方は例えば Apple の AppStore のように iPhone 使えるアプリがひとまとめになっているサイトのようなものの python 版だと考えてください。
これによって import している各ライブラリが使えるようになります。

```python
pip install compute_rhino3d rhino3dm
```

#### RhinoCompute のサーバーの指定

以下の箇所では、RhinoCompute のサーバーを指定しています。

```python
compute_rhino3d.Util.url = 'http://localhost:6500/'
```

Hops がインストールされている環境では、Grasshopper を起動すると裏で自動で RhinoCompute のサーバーが上記 URL で起動するので、基本的には特に操作する必要はありません。

#### 入力の値を指定

以下の箇所では入力の値を指定しています。

```python
# create DataTree for each input
input_trees = []
tree = gh.DataTree("A")
tree.Append([0], ["10.0"])
input_trees.append(tree)

tree = gh.DataTree("B")
tree.Append([0], ["5.0"])
input_trees.append(tree)
```

`tree = gh.DataTree("A")` の箇所では Hops の A の入力の箇所の値を指定しています。
Export する時の画像を確認していただくと A には 10 の値が入力されていることが分かると思います。
ですので別の計算を行いたかったら、`tree.Append([0], ["10.0"])` の箇所の 10.0 の箇所を変えれば別の結果を得ることができます。

`tree = gh.DataTree("B")` の箇所も A と同様の内容です。

#### 計算の実行

以下の箇所で grasshopper で計算を実行しています。

```python
output = gh.EvaluateDefinition('Path/to/Desktop/sum.gh', input_trees)
```

メソッドの名称からもわかるように grasshopper の ファイル（definition）を評価（Evaluate）しています。

output には計算の実行結果が入っています。

#### 結果の処理

以下の箇所で結果の出力のための処理をしています。

```python
# error を取得
errors = output['errors']
if errors:
    print('ERRORS')
    for error in errors:
        print(error)

# warning を取得
warnings = output['warnings']
if warnings:
    print('WARNINGS')
    for warning in warnings:
        print(warning)

# 結果の値を取得
values = output['values']
for value in values:
    name = value['ParamName']
    inner_tree = value['InnerTree']
    # 出力の名前を出力（例えば RH_OUT:result）
    print(name)
    for path in inner_tree:
        # 結果のデータツリーでのパスを出力
        print(path)
        values_at_path = inner_tree[path]
        for value_at_path in values_at_path:
            data = value_at_path['data']
            # 結果を出力
            if isinstance(data, str) and 'archive3dm' in data:
                obj = rhino3dm.CommonObject.Decode(json.loads(data))
                print(obj)
            else:
                print(data)
```

#### 計算を実行する

pip を使って必要なライブラリをインストールできていれば、以下を実行するればこれらのコードが流れます。

```python
python ./sum.py
```

問題なく処理が実行されると以下のように結果が返ってきます。

```
RH_OUT:result
{0}
15.0
```

今回は出力を RH_OUT:result しか作っていないので結果は一つですが、それぞれの結果の名前、データツリーでのパス、結果を出力することができます。

#### 複数の結果を取得してみる

これでは Grasshopper でそのまま流すことと変わらないので、for 文を使って複数の処理を流してみます。

```python
import compute_rhino3d.Util
import compute_rhino3d.Grasshopper as gh
import rhino3dm
import json

compute_rhino3d.Util.url = 'http://localhost:6500/'

# for 文を追加
for i in range(1,5):
    input_trees = []
    tree = gh.DataTree("A")

    # もともと 10.0 を入力していたが、
    # i を入力することで、for文中で値を変える
    tree.Append([0], [i])
    input_trees.append(tree)

    tree = gh.DataTree("B")
    tree.Append([0], ["5.0"])
    input_trees.append(tree)

    output = gh.EvaluateDefinition('./sum.gh', input_trees)

    # 以降変化なし
```

こちらを実行すると i が 1 から 4 に変化し 4 回計算が流れるので、以下のような結果が返ってきます。
これで少しコードで処理する利点が出たのではないでしょうか。

```
RH_OUT:result
{0}
6.0
RH_OUT:result
{0}
7.0
RH_OUT:result
{0}
8.0
RH_OUT:result
{0}
9.0
```

### Python で最適化を実行する

#### optuna について

Python にはたくさんの最適化ライブラリが存在します。
ここではハイパーパラメータ最適化に使われる Optuna を使います。
Optuna は上で紹介した Tunny の内部で使用しているライブラリでもあります。

- [公式サイト](https://www.preferred.jp/ja/projects/optuna/)

開発は PreferredNetworks という日本の会社で、AI や機械学習などでトップを行くスタートアップです。
GitHub の OSS として開発されており、現在も積極的に開発されていることから Tunny に採用しています。

#### 実行環境の構築

RhinoCompute で Grasshopper を実行する箇所でやったように、pip を使って optuna をインストールします。

```python
pip install optuna
```

//TODO: 続きをかく

#### 連携用の Karamba3d モデルの作成

上で最適化を実行した Karamba3d のモデルを変更して、Python から実行できるようにします。

//TODO: 続き

#### Jupyter Notebook 化

//TODO: これでやりたいよね。コードの社内資料化という意味でも。Colab でやりたいけど、ローカル通信は大変そう

#### Python から最適化の実行

//TODO: 続き

### Deep Dive

今回は最適化の例をやったため、Grasshopper 上で最適化コンポーネントを使った際とやっていることは大きく変わりません。
Python にはデータサイエンスや機械学習のライブラリがあり、近年ではこれらを使ってより効率的に解を取得する方法が行われています。
例えば KPF の以下の取り組みがあります。

- [Bridging Data Science and Architectural Practice](https://medium.com/@kpfui/bridging-data-science-and-architectural-practice-aceb3f23fd95)

プログラムを使った RhinoCompute と Grasshopper の連携そのものへの理解をより深めたい方は、公式でサポートされていないプログラム言語である Rust から RhinoCompute を実行する方法を以下の記事で紹介しているので、こちらの記事を読んでいただくと参考になります。

- [Deep dive into RhinoCompute through Rust](https://hiron.dev/articles/deep-dive-into-rhinocompute-through-rust)

## 質疑応答コーナー

本日の内容は以上です。
質疑などありますか？
