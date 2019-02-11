import os
import sys
import MySQLdb
import sql as qb #query builder
import numpy as np
import time
import warnings

class BaseDBManager(object):
    def __init__(self):
        self.cursor = None
        self.connection = None

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def with_connection(func):
        """Decorator to make database connections."""
        def wrapped(self,*args,**kwargs):
            if self.connection is None:
                try:
                    self.connection = self.connect()
                    self.cursor = self.connection.cursor()
                except Exception as error:
                    self.cursor = None
                    raise error
            else:
                self.connection.ping(True)
            func(self,*args,**kwargs)
        return wrapped

    @with_connection
    def execute_query(self,query):
        """Execute a mysql query"""
        try:
            self.cursor.execute(query)
        except Exception as error:
            raise error
            #warnings.warn(str(error),Warning)

    @with_connection
    def execute_insert(self,insert):
        """Execute a mysql insert/update/delete"""
        try:
            self.cursor.execute(insert)
            self.connection.commit()
        except Exception as error:
            self.connection.rollback()
            raise error
            #warnings.warn(str(error),Warning)

    @with_connection
    def execute_many(self,insert,values):
        #values is list of tuples
        try:
            self.cursor.executemany(insert,values)
            self.connection.commit()
        except Exception as error:
            self.connection.rollback()
            raise error

    def lock(self,lockname,timeout=5):
        self.execute_query("SELECT GET_LOCK('%s',%d)"%(lockname,timeout))
        response = self.get_output()
        return bool(response[0][0])

    def release(self,lockname):
        self.execute_query("SELECT RELEASE_LOCK('%s')"%(lockname))

    def execute_delete(self,delete):
        self.execute_insert(delete)

    def close(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = None

    def fix_duplicate_field_names(self,names):
        """Fix duplicate field names by appending
        an integer to repeated names."""
        used = []
        new_names = []
        for name in names:
            if name not in used:
                new_names.append(name)
            else:
                new_name = "%s_%d"%(name,used.count(name))
                new_names.append(new_name)
            used.append(name)
        return new_names

    def get_output(self):
        """Get sql data in numpy recarray form."""
        if self.cursor.description is None:
            return None
        names = [i[0] for i in self.cursor.description]
        names = self.fix_duplicate_field_names(names)
        try:
            output  = self.cursor.fetchall()
        except Exception as error:
            warnings.warn(str(error),Warning)
            return None
        if not output or len(output) == 0:
            return None
        else:
            output = np.rec.fromrecords(output,names=names)
            return output


class SuperbDataBase(BaseDBManager):
    __HOST = "<host>"
    __NAME = "<name>"
    __USER = "<user>"
    __PASSWD = "<password>"
    def __init__(self):
        super(SuperbDataBase,self).__init__()

    def connect(self):
        return MySQLdb.connect(
            host=self.__HOST,
            db=self.__NAME,
            user=self.__USER,
            passwd=self.__PASSWD)

    def get_obs_id_from_utc_and_beam(self,utc,beam):
        beam = int(beam)
        obs = qb.Table("Observations")
        select = obs.select(obs.obs_id)
        select.where = (obs.utc_start == utc) & (obs.beam == beam)
        query,args = tuple(select)
        return query%args

    def get_beam_id_from_path(self,path):
        """Get a beam ID from a path of type: ../YYYY-MM-DD-hh:mm:ss/BEAM_NO."""
        utc,beam = path.split("/")[-2:]
        utc_str = "%s %s"%(utc[:10],utc[11:])
        condition = "utc_start LIKE '%s' AND beam LIKE '%s'"%(utc_str,beam)
        return self.get_single_value("beam_id","beams",condition)

    def get_survey_id(self,description):
        condition = "name LIKE '%s'" % description
        return self.get_single_value("type_id","types",condition)

    def get_user_id(self,username):
        condition = "user_name LIKE '%s'" % username
        return self.get_single_value("id","uc_users",condition)

    def create_new_software_config_id(self,name,version,path):
        cols = ["name","version","path_to_archive"]
        values = ["'%s'"%name,"'%s'"%version,"'%s'"%path]
        self.simple_insert("processing_software_config",cols,values)

    def get_software_config_id(self,name,version,path):
        condition = "name LIKE '%s' AND version like '%s' AND path_to_archive LIKE '%s'" % (name,version,path)
        version_id = self.get_single_value("id","processing_software_config",condition)
        if version_id is None:
            self.create_new_software_config_id(name,version,path)
            version_id = self.get_single_value("id","processing_software_config",condition)
        return version_id

    def create_new_output_dir_id(self,path):
        cols = ["path"]
        values = ["'%s'"%path]
        self.simple_insert("processing_output_dir",cols,values)

    def get_output_dir_id(self,path):
        condition = "path LIKE '%s'" % path
        dir_id = self.get_single_value("id","processing_output_dir",condition)
        if dir_id is None:
            self.create_new_output_dir_id(path)
            dir_id = self.get_single_value("id","processing_output_dir",condition)
        return dir_id

    def create_new_process_type_id(self,name):
        cols = ["name"]
        values = ["'%s'"%name]
        self.simple_insert("processing_type",cols,values)

    def get_process_type_id(self,name):
        condition = "name LIKE '%s'" % name
        p_id = self.get_single_value("id","processing_type",condition)
        if p_id is None:
            self.create_new_process_type_id(name)
            p_id = self.get_single_value("id","processing_type",condition)
        return p_id

    def create_new_hardware_config_id(self,cudart,cuda_driver,card_type):
        cols = ["cuda_runtime_version","cuda_driver_version","gpu_type"]
        values = ["'%s'"%cudart,"'%s'"%cuda_driver,"'%s'"%card_type]
        self.simple_insert("processing_hardware",cols,values)

    def get_hardware_config_id(self,cudart,cuda_driver,card_type):
        condition = "cuda_runtime_version LIKE '%s' AND cuda_driver_version LIKE '%s' AND gpu_type LIKE '%s'" % (
            cudart,cuda_driver,card_type)
        hardware_id = self.get_single_value("id","processing_hardware",condition)
        if hardware_id is None:
            self.create_new_hardware_config_id(cudart,cuda_driver,card_type)
            hardware_id = self.get_single_value("id","processing_hardware",condition)
        return hardware_id

    def create_job_info_known_id(self,
                                 beam_id,
                                 user_id,
                                 software_config_id,
                                 output_dir_id,
                                 processing_type_id):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        cols = ["beam_id",
                "user_id",
                "processing_software_config_id",
                "processing_output_dir_id",
                "processing_type_id",
                "submit_time"]
        values = [str(beam_id),
                  str(user_id),
                  str(software_config_id),
                  str(output_dir_id),
                  str(processing_type_id),
                  "'%s'"%(now)]
        self.simple_insert("processing",cols,values)
        condition = "beam_id=%s AND submit_time LIKE '%s'"%(beam_id,now)
        return self.get_single_value("id","processing",condition)

    def create_job_info(self,
                        beam_id,
                        username,
                        software_name,
                        software_version,
                        software_path,
                        base_output_path,
                        processing_type):
        cols = ["beam_id",
                "user_id",
                "processing_software_config_id",
                "processing_output_dir_id",
                "processing_type_id",
                "submit_time"]
        beam_id            = str(beam_id)
        user_id            = str(self.get_user_id(username))
        software_config_id = str(self.get_software_config_id(software_name,software_version,software_path))
        output_dir_id      = str(self.get_output_dir_id(base_output_path))
        processing_type_id = str(self.get_process_type_id(processing_type))
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        values = [beam_id,
                  user_id,
                  software_config_id,
                  output_dir_id,
                  processing_type_id,
                  "'%s'"%(now)]
        self.simple_insert("processing",cols,values)
        condition = "beam_id=%s AND submit_time LIKE '%s'"%(beam_id,now)
        return self.get_single_value("id","processing",condition)

    def update_folding_job_start_info(self,utc):
        cols = ["folding_start_time"]
        values = ["NOW()"]
        condition = "utc_start LIKE '%s'"%(utc)
        self.simple_update("processing p LEFT OUTER JOIN beams b ON (b.beam_id = p.beam_id)",cols,values,condition)

    def update_job_start_info(self,
                              processing_id,
                              cudart,
                              cuda_driver,
                              card_type,
                              hostname,
                              device_id):
        cols = ["processing_hardware_id",
                "hostname",
                "devices_used",
                "start_time"]
        hardware_id = self.get_hardware_config_id(cudart,cuda_driver,card_type)
        values = [hardware_id,
                  "'%s'"%hostname,
                  "'%s'"%device_id,
                  "NOW()"]
        condition = "id=%d"%(processing_id)
        self.simple_update("processing",cols,values,condition)

    def update_job_end_info(self,processing_id,success=True):
        cols = ["end_time",
                "success"]
        values = ["NOW()",
                  int(success)]
        condition = "id=%d"%(processing_id)
        self.simple_update("processing",cols,values,condition)

    def update_folding_job_end_info(self,utc,success=True):
        cols = ["folding_end_time",
                "folded"]
        values = ["NOW()",
                  int(success)]
        condition = "utc_start LIKE '%s'"%(utc)
        self.simple_update("processing p LEFT OUTER JOIN beams b ON (b.beam_id = p.beam_id)",cols,values,condition)
