# -*- coding: utf-8 -*-

import input_data
import tensorflow as tf

mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)     #下载并加载mnist数据
x = tf.placeholder(tf.float32, [None, 784])                        #输入的数据占位符
y_actual = tf.placeholder(tf.float32, shape=[None, 10])            #输入的标签占位符


# 定义一个函数，用于初始化所有的权值 W
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


# 定义一个函数，用于初始化所有的偏置项 b
def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


# 对于卷积层，我们选择vanilla版本。我们的卷积使用步长为1且进行0填充操作，以保证输出和原输入size相同。
# 定义一个函数，用于构建卷积层
# tf.nn.conv2d(input, filter, strides, padding, use_cudnn_on_gpu=None, data_format=None, name=None)
# 实现输入input和卷积核filter之间的卷积操作。
# 注意input和filter中tensor各维度的顺序：
# 　input: [batch, in_height, in_width, in_channels]
# 　filter: [filter_height, filter_width, in_channels, out_channels]
# 卷积结果的输出维度计算：
# 当padding=’SAME’时：
# 　out_height = ceil(float(in_height) / float(strides[1]))
# 　out_width = ceil(float(in_width) / float(strides[2]))
# 当padding=’VALID’时：
# out_height = ceil(float(in_height - filter_height + 1) / float(strides[1]))
# out_width = ceil(float(in_width - filter_width + 1) / float(strides[2]))
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


# Our pooling is plain old max pooling over 2x2 blocks .
# 定义一个函数，用于构建池化层
def max_pool(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


#构建网络
#在创建第一个卷积层之前，我们需要将输入数据x reshape成一个4维张量，其中的第2/3维对应着图像的width和height，最后一维代表图片的颜色通道数(因为是灰度图所以这里的通道数为1，如果是rgb彩色图，则为3)。
#把输入x(二维张量,shape为[batch, 784])变成4d的x_image，x_image的shape应该是[batch,28,28,1]
#-1表示自动推测这个维度的size,表示一次输入计算的数量
x_image = tf.reshape(x, [-1,28,28,1])         #转换输入数据shape,以便于用于网络中
#初始化W为[5,5,1,32]的张量，表示卷积核大小为5*5，第一层网络的输入和输出神经元个数分别为1和32
W_conv1 = weight_variable([5, 5, 1, 32])
#初始化b为[32],即输出大小
b_conv1 = bias_variable([32])
# 我们把x_image和权值向量进行卷积，加上偏置项，然后应用ReLU激活函数，最后进行max pooling。.The max_pool_2x2 method
# will reduce the image size to 14x14.
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)     #第一个卷积层
#h_pool1的输出即为第一层网络输出，shape为[batch,14,14,1]
h_pool1 = max_pool(h_conv1)                                  #第一个池化层

#为了构建一个更深的网络，我们会把几个类似的层堆叠起来。第二层中，每个5x5的patch会得到64个特征。
#第2层，卷积层
#卷积核大小依然是5*5，这层的输入和输出神经元个数为32和64
W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)      #第二个卷积层
#h_pool2即为第二层网络输出，shape为[batch,7,7,1]
h_pool2 = max_pool(h_conv2)                                   #第二个池化层

#现在，图片尺寸减小到7x7，我们加入一个有1024个神经元的全连接层，用于处理整个图片。我们把池化层输出的张量reshape成一些向量，乘上权重矩阵，加上偏置，然后对其使用ReLU。
#W的第1维size为7*7*64，7*7是h_pool2输出的size，64是第2层输出神经元个数
W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])
#计算前需要把第2层的输出reshape成[batch, 7*7*64]的张量
#-1代表的含义是不用我们自己指定这一维的大小，函数会自动算
h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])              #reshape成向量
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)    #第一个全连接层

# 为了减少过拟合，我们在输出层之前加入dropout。
# 我们用一个placeholder来代表一个神经元的输出在dropout中保持不变的概率。
# 这样我们可以在训练过程中启用dropout，在测试过程中关闭dropout。
# TensorFlow的tf.nn.dropout操作除了可以屏蔽神经元的输出外，还会自动处理神经元输出值的scale。
# 所以用dropout的时候可以不用考虑scale。
keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)                  #dropout层

#最后，我们添加一个softmax层。
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])
y_predict=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)   #softmax层

#预测值和真实值之间的交叉墒
cross_entropy = -tf.reduce_sum(y_actual*tf.log(y_predict))     #交叉熵
#train op, 使用ADAM优化器来做梯度下降。学习率为0.0001
train_step = tf.train.GradientDescentOptimizer(1e-3).minimize(cross_entropy)    #梯度下降法
# train_step = tf.train.AdagradOptimizer(1e-5).minimize(cross_entropy)
#评估模型，tf.argmax能给出某个tensor对象在某一维上数据最大值的索引。
#因为标签是由0,1组成了one-hot vector，返回的索引就是数值为1的位置
correct_prediction = tf.equal(tf.argmax(y_predict,1), tf.argmax(y_actual,1))
#计算正确预测项的比例，因为tf.equal返回的是布尔值，
#使用tf.cast把布尔值转换成浮点数，然后用tf.reduce_mean求平均值
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))                 #精确度计算
#创建一个交互式Session
sess=tf.InteractiveSession()
#初始化变量
sess.run(tf.initialize_all_variables())
#开始训练模型，循环20000次，每次随机从训练集中抓取50幅图像
for i in range(20000):
  batch = mnist.train.next_batch(50)
  if i%100 == 0:                  #训练100次，验证一次
    #每100次输出一次日志
    train_acc = accuracy.eval(feed_dict={x:batch[0], y_actual: batch[1], keep_prob: 1.0})
    print "step %d, training accuracy %g" % (i, train_acc)
    train_step.run(feed_dict={x: batch[0], y_actual: batch[1], keep_prob: 0.5})

test_acc=accuracy.eval(feed_dict={x: mnist.test.images, y_actual: mnist.test.labels, keep_prob: 1.0})
print("test accuracy",test_acc)