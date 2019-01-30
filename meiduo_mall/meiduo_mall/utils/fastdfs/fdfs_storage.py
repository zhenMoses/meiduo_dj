from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client




class FastDFSStorage(Storage):
    """自定义文件存储系统类"""

    def __int__(self):
        """初始化方法"""

        pass

    def _open(self,name,mode='rb'):
        """打文件,但是我们自定义文件存储系统类的目的,只是为了上传和下传,不需要打开,所以此方法什么也不做,直接pass"""
        pass

    def _save(self,name,content):
        """
        上传图片时调用此方法
        :param name: 要上传的文件名字
        :param content: 要上传的文件对象,将来可以通过content.read() 读取到文件的二进制数据
        :return: 返回file_id将来会自动存储到image字段
        """

        # 1.创建fdfs客户端
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')

        # 2.上传文件
        ret = client.upload_appender_by_buffer(content.read())
        # 3.安全判断
        if ret.get('Status') !='Upload successed.':
            raise Exception('文件上传失败')

        # 4.返回file_id
        return ret.get('Remote file_id')

    def exists(self, name):
        """
        判断要上传的文件是否已存在,如果存在就不上传了,不存在再进行调用save方法上传
        :param name: 要进行判断上不上传的文件名
        :return: True或False 如果返回False表示此方法不存在,就上传,如果返回True表示文件已存在就不上传
        """
        return False

    def url(self, name):
        """
        当访问image字段的url属性时,就会自动调用此url方法拼接好文件的完整url路径
        :param name: 此name是当初save方法中返回的file_id
        :return: storage ip:端口 + file_id
        """
        return 'http://192.168.239.162:8888/' + name

    """
    {'Group name': 'group1',
     'Remote file_id': 'group1/M00/00/00/wKhn0lxNDMiAeS9zAAC4j90Tziw48.jpeg',
     'Status': 'Upload successed.',
     'Local file name': '/Users/chao/Desktop/01.jpeg',
     'Uploaded size': '46.00KB',
     'Storage IP': '192.168.103.210'}

    """

