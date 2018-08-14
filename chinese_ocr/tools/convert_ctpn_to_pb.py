# coding=UTF-8
import tensorflow as tf
import os.path
import argparse
from tensorflow.python.framework import graph_util

MODEL_DIR = "pb_models"
MODEL_NAME = "text_detect_model.pb"

if not tf.gfile.Exists(MODEL_DIR):  # 创建目录
    tf.gfile.MakeDirs(MODEL_DIR)

def freeze_graph(model_folder):
    checkpoint = tf.train.get_checkpoint_state(model_folder)  # 检查目录下ckpt文件状态是否可用
    input_checkpoint = checkpoint.model_checkpoint_path  # 得ckpt文件路径
    output_graph = os.path.join(MODEL_DIR, MODEL_NAME)  # PB模型保存路径
    output_node_names = ['rpn_cls_score/Reshape_1', 'Reshape_2', 'rpn_cls_prob', 'rpn_bbox_pred/Reshape_1']  # 原模型输出操作节点的名字
    saver = tf.train.import_meta_graph(input_checkpoint + '.meta',
                                       clear_devices=True)  # 得到图、clear_devices ：Whether or not to clear the device field for an `Operation` or `Tensor` during import.

    graph = tf.get_default_graph()  # 获得默认的图
    input_graph_def = graph.as_graph_def()  # 返回一个序列化的图代表当前的图

    with tf.Session() as sess:
        saver.restore(sess, input_checkpoint)  # 恢复图并得到数据
        f = open('input_graph_def.txt', 'w')
        f.write(str(input_graph_def))

        output_graph_def = graph_util.convert_variables_to_constants(  # 模型持久化，将变量值固定
            sess,
            input_graph_def,
            output_node_names
        )
        with tf.gfile.GFile(output_graph, "wb") as f:  # 保存模型
            f.write(output_graph_def.SerializeToString())  # 序列化输出
        print("%d ops in the final graph." % len(output_graph_def.node))  # 得到当前图有几个操作节点

        for op in graph.get_operations():
            print(op.name, op.values())


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("model_folder", type=str, help="input ckpt model dir")  # 命令行解析，help是提示符，type是输入的类型，
#     # 这里运行程序时需要带上模型ckpt的路径，不然会报 error: too few arguments
#     aggs = parser.parse_args()
#     freeze_graph(aggs.model_folder)

freeze_graph("../ctpn/models") #模型目录