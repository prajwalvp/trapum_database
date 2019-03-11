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


class TrapumDataBase(BaseDBManager):
    __HOST = "127.0.0.1"
    __NAME = "trapum_28feb19"
    __USER = "root"
    __PASSWD = "passwd"
    def __init__(self):
        super(TrapumDataBase,self).__init__()

    def connect(self):
        return MySQLdb.connect(
            host=self.__HOST,
            db=self.__NAME,
            user=self.__USER,
            passwd=self.__PASSWD)


     #Before Observations
    def create_new_project(self,**kwargs):
        """
        @brief   Creates new project entry in Projects table     

        @params  name    Name of the project             
        @params  notes   any extra information for the project 
        """ 
        cols=["name","notes"] 
        values = [kwargs['name'],kwargs['notes']]
        self.simple_insert("Projects",cols,values)

    def create_new_beamformer_config(self,**kwargs):
        """
        @brief   Creates a new beamformer configuration entry in the Beamformer Configurations table  

        @params  centre_freq    Observation frequency in MHz 
        @params  bw             Bandwidth used in MHz
        @params  nchans         Number of channels
        @params  tsamp          Sampling time in us
        @params  receiver       Receiver used
        @params  metadata       Info on other parameters as a key,value pair
        """ 
        cols=["`centre_frequency`","`bandwidth`","`nchans`","`tsamp`","`receiver`","`metadata`"]
        values = [kwargs['centre_frequency'],kwargs['bandwidth'],kwargs['nchans'],kwargs['tsamp'],kwargs['receiver'],kwargs['metadata']]
        self.simple_insert("Beamformer_Configuration",cols,values)


    def create_new_target(self,**kwargs):
        """
        @brief   Creates new target entry in Targets table

        @params  project_id      Project name identifier
        @params  source_name     Name of source to be observed
        @params  ra              Right Ascension in HH::MM::SS
        @params  dec             Declination in DD::MM::SS
        @params  region          Name of specific sky region e.g. globular cluster
        @params  semi_major_axis Length of semi major axis of elliptic target region (in arcseconds) ??
        @params  semi_minor_axis Length of semi minor axis of elliptic target region (in arcseconds) ??
        @params  position_angle  Angle of source w.r.t plane of sky (in degrees)
        @params  metadata        Info on other parameters as key,value pair       
        @params  notes           Any extra info about the target    
        """ 
        cols = ["`project_id`","`source_name`","`ra`","`dec`","`region`","`semi_major_axis`","`semi_minor_axis`","`position_angle`","`metadata`","`notes`"]
        values = [kwargs['project_id'],kwargs['source_name'],kwargs['ra'],kwargs['dec'],kwargs['region'],kwargs['semi_major_axis'],kwargs['semi_minor_axis'],
                  kwargs['position_angle'],kwargs['metadata'],kwargs['notes']]
        self.simple_insert("Targets",cols,values)

    # During Observations
    def create_new_pointing(self,**kwargs):
        """
        @brief   Creates new pointing entry in Pointings table     

        @params  target_id    Unique target identifier
        @params  bf_config_id Unique configuration identifier
        @params  tobs         Length of observation (in seconds) 
        @params  utc_start    UTC start time of observation HH:MM:SS
        @params  sb_id        Unique schedule block identifier
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """ 
         
        cols = ["`target_id`","`bf_config_id`","`tobs`","`utc_start`","`sb_id`","`metadata`","`notes`"]     
        vals = [kwargs['target_id'],kwargs['bf_config_id'],kwargs['tobs'],kwargs['utc_start'],kwargs['sb_id'],kwargs['metadata'],kwargs['notes']]
        self.simple_insert("Pointings",cols,vals)

    # After observations
    
    def create_new_beam(self,**kwargs):
        """
        @brief   Creates new Beam entry in Beams table     

        @params  Name       Unique pointing identifer for beam             
        @params  on_target  indicates if beam is on or off target: 1 for on 0 for off
        @params  ra         Right Ascension in HH::MM::SS of beam
        @params  dec        Declination in DD::MM::SS of beam
        @params  coherent  indicates if beam is coherent or incoherent: 1 for coherent on 0 for incoherent
        """ 
        cols = ["`pointing_id`","`on_target`","`ra`","`dec`","`coherent`"]
        vals = [kwargs['pointing_id'],kwargs['on_target'],kwargs['ra'],kwargs['dec'],kwargs['coherent']]
        self.simple_insert("Beams",cols,vals)


    def update_tobs(self,**kwargs):
        """
        @brief   Update length of observation in Pointings table

        @params  pointing_id    Unique pointing identifer 
        @params  tobs           value of observation time
        """ 
        cols = "tobs"
        values = kwargs['tobs']
        condition = "pointing_id = %f"%kwargs['pointing_id'] # update tobs for particular pointing id 
        self.simple_update("Pointings",cols,values,condition)


    def create_new_dataproduct(self,**kwargs):
        """
        @brief   Create data product entry in Data_Products table

        @params  pointing_id    Unique pointing identifer 
        @params  beam_id        Unique Beam identifier
        @params  processing_id  Unique processing identifier,NULL if recorded from observation
        @params  file_status    If file exists or not: 1 if exists, 0 if deleted,  
        @params  filepath       Path to file
        @params  file_type      Type of file produced 
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """ 
        """initiate processings_id to a default value,parent_id to 0,file_status=to_be_processed,get filepath and type from obs table,metadata is 0"""
        cols=["pointing_id","beam_id","processing_id","file_status","filepath","file_type","metadata","notes"]
        values=[kwargs['pointing_id'],kwargs['beam_id'],kwargs['processing_id'],kwargs['file_status'],kwargs['filepath'],kwargs['file_type'],kwargs['metadata'],kwargs['notes']]
        self.simple_insert("Data_Products",cols,values)
        

    def create_new_processing(self,**kwargs):
        """
        @brief   Create new processing entry in Processings table
        
        @params  processing_id  Unique processing identifier
        @params  pointing_id    Unique pointing identifer 
        @params  pipeline_id    Unique pipeline identifer 
        @params  hardware_id    Unique hardware identifer 
        @params  submit_time    time of submitting job to queue (YYYY-MM-DD HH:MM:SS)
        @params  start_time     Start time of processing (YYYY-MM-DD HH:MM:SS)
        @params  end_time       End time of processing (YYYY-MM-DD HH:MM:SS)
        @params  process_status Status of the process. Options are : 0->submitted, 1->processing, 2->completed successfully, 3-> completed but failed
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """ 
        """initiate processings_id to a default value,parent_id to 0,file_status=to_be_processed,get filepath and type from obs table,metadata is 0"""
        """ pipeline_id = ?,hardware_id=?, dp_id = get from DP table, submit_time = when job submitted update, 
        start_time = when pipeline starts , update,end_time=0 then update after end, process_status= submitted->processing->completed,metadata=0 """

        cols = ["pointing_id","pipeline_id","hardware_id","submit_time","start_time","end_time"
                ,"process_status","metadata","notes"]
        vals=[kwargs['pointing_id'],kwargs['pipeline_id'],kwargs['hardware_id'],kwargs['submit_time'],kwargs['start_time'],
              kwargs['end_time'],kwargs['process_status'],kwargs['metadata'],kwargs['notes']]
        self.simple_insert("Processings",cols,vals)

    def update_submit_time(self,submit_time):
        """
        @brief Update the time of job submission to RabbitMQ

        @params value of submission time (YYYY-MM-DD HH:MM:SS)  
        """
        cols = ["submit_time"]
        values=["%s"%start_time]
        condition = ""
        self.simple_update("Processings",cols,values,condition)
       

    def update_process_status(self,process_status):
        """
        @brief Update the status of a particular processing.Options are : 0->submitted, 1->processing, 2->completed

        @params Value indicating status: (YYYY-MM-DD HH:MM:SS)  
        """
        cols = ["process_status"]
        values=["%s"%process_status]
        condition = ""  #(?)
        self.simple_update("Processings",cols,values,condition)


  
    def create_new_pipeline(self,**kwargs):
        """
        @brief   Creates new pipeline entry in Pipelines table     

        @params  hash    unique hash of pipeline                 
        @params  name    unique name of pipeline e.g. presto,peasoup                 
        @params  notes   any extra information for the project 
        """ 
        cols = ["hash","name","notes"]
        values = [kwargs['hash'],kwargs['name'],kwargs['notes']]
        self.simple_insert("Pipelines",cols,values)
    
    def create_new_pivot(self,**kwargs):
        """
        @brief   Creates new pivot entry in Processing_Pivot table     

        @params  dp_id          Unique dataproducts identifier 
        @params  processing_id  unique Processings identifier                
        """ 
        cols = ["dp_id","processing_id",]
        values = [kwargs['dp_id'],kwargs['processing_id']]
        self.simple_insert("Processing_Pivot",cols,values)

    def update_start_time(self,start_time):
        cols = ["start_time"]
        values=["%s"%start_time]
        condition = "Pipeline_start + start_time=0" 
        self.simple_update("Processings",cols,values)
        
   
    def create_new_hardware_config(self,**kwargs):
        """
        @brief   Creates new hardware configuration in Hardwares table  
    
        @params  name         Name of hardware device 
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """
        cols = ["name","metadata","notes"]
        values = [kwargs['name'],kwargs['metadata'],kwargs['notes']]
        self.simple_insert("Hardwares",cols,values)

    
    # End of pipeline run 
    
   
    def update_end_time(self,end_time):
        cols = ["end_time"]
        values = ["%s"%end_time]
        condition = "Pipeline run over and end_time = 0" 
        self.simple_update("Processings",cols,vals,condition)
    
    # Update new dp_id with parent_id reference




  
    def update_file_status(self,name):
        cols = ["file_status"]
        values = ["%s" %name]
        condition = "trigger from user interaction/~processings_id = None "%()     
        self.simple_update("Data_Products",cols,values,condition)

    def update_process_status(self,description):
        cols = ["process_status"]
        values = ["%s" %description]
        condition = "trigger from user interaction/~processings_id = None "%()     
        self.simple_update("Processings",cols,values,condition)
 
    def simple_insert(self,table,cols,values):
        """
        @brief   Inserts new entry into respective table   
    
        @params  table        Table for new entry
        @params  cols         Columns in table to be changed
        @params  values       values for the respective columns to be added
        """
        columns = str(tuple(cols)).replace('\'','')
        vals = str(tuple(values)).replace('\"','')
        print columns
        print vals
        print "INSERT INTO %s%s VALUES %s"%(table,columns,vals) 
        self.execute_insert("INSERT INTO %s%s VALUES %s"%(table,columns,vals)) 

    def simple_update(self,table,cols,values,condition):
        """
        @brief   Updates existing entry in respective table   
    
        @params  table        Table to update
        @params  cols         Columns in table to be updated
        @params  values       values for the respective columns to be updated
        """
        self.execute_insert("UPDATE %s set %s=%s WHERE %s"%(table,cols,values,condition))
        
    def get_values(self,table,cols,condition):
        """
        @brief   Updates existing entry in respective table   
    
        @params  table        Table to analyse
        @params  cols         Columns in table to be checked
        @params  values       values for the respective columns to be retrieved

        @return  list of values requested
        """ 
        self.execute_query("select %s from %s where %s"%(cols,table,condition))
        output =  self.cursor.fetchall()
        vals=[]
        for i in range(len(output)):
            vals.append(list(list(output)[i])[0])
        return vals


################ Useful Functions ########################

    
    def get_project_id(self,description):
        """
        @brief   Retrieve name of project

        @params  description   Name of project (need not be exact)   
        
        @return  project identifier number  
        """
        condition = "name LIKE '%s'" % description
        return self.get_values("Projects","project_id",condition)
 
    def get_beam_ids_for_pointing(self,pointing_id):
        """
        @brief   Retrieve all beams for particular pointing

        @params  pointing_id   pointing identifier number
        
        @return  list of beam identifier values  
        """
        condition = "pointing_id LIKE '%s'" %pointing_id
        return self.get_values("Beams","beam_id",condition)

    def get_non_processed_data_products(self): 
        """
        @brief   Retrieve data_products which have not been processed at all
        
        @return  list of Data Product identifier values 
        """
        condition = "processing_id IS NULL"
        return self.get_values("Data_Products","dp_id",condition)

    def get_data_products_for_pointing(self,pointing_id):
        """
        @brief   Retrieve data products for particular pointing

        @params  pointing_id          pointing identifier number
        
        @return  list of data product identifier values
        """
        condition = "pointing_id LIKE %s"%pointing_id
        return self.get_values("Data_Products","dp_id",condition)

    def get_pointings_for_target(self,target_id):
        """
        @brief   Retrieve pointings for particular target 

        @params  target_id    target identifier number
        
        @return  list of pointing identifier values
        """
        condition = "target_id LIKE %s"%target_id
        return self.get_values("Pointings","pointing_id",condition)

    def get_data_products_from_processing(self,processing_id):
        """
        @brief   Retrieve data products from particular processing

        @params  processing_id   processing identifier value 
        
        @return  list of data product identifier values 
        """
        condition = "processing_id LIKE %s"%processing_id
        return self.get_values("Processing_Pivot","dp_id",condition)  

   


if __name__ =='__main__':
    trapum = TrapumDataBase();
    c = trapum.connect()
    c1 = c.cursor()
    ####  Preparation for observation ####

    ##Targets and Projects will already be filled
    
    ## Create new beamformer configuration
    trapum1.create_new_beamformer_config() #args to be filled

    #### Observatiion has begun ####

    ## Create_new_pointing
    trapum1.create_new_pointing(..)

    ## Create new Beams
    trapum.create_new_beam(..)

    ###### Observation has ended #########

    ## Update tobs 
    trapum1.update_tobs(current_time,condition) # Trigger that observation is over (how?) and how to get timestamp for tobs (time.strftime) ?

    ##### Create new dataproduct #######
    trapum1.create_new_dataproduct(..) # processing_id =NULL,file_status= to be processed, filetype and path from obs table 

    
    ######create new processing_id
    trapum1.create_new_processing_id(..)  # processing_id=NULL, rest retrievable .. Assume that pipeline and hardware already available in tables(?)

    #### Update submit time
    trapum1.update_submit_time(...) # Trigger once job details (file path etc etc) submitted to rabbitmq

    #trapum1.create_new_hardware_config_id ## 
    trapum1.create_new_hardware_config

    ### Update process status

    trapum1.update_process_status(0)

    ## Start of pipeline -- once consumed from rabbitmq

    trapum1.create_new_processing_id(..)  # processing_id=NOT NULL, rest retrievable .. Assume that pipeline and hardware already available in tables(?)
    
    trapum1.create_new_pipeline_id(...)

    trapum1.update_start_time (..) # Timestamps?

    trapum1.update_process_status(1)
    #

    ## End of pipeline run

    trapum1.update_end_time(..)   

    trapum1.update_process_status(2/3) # Update success if in success queue, or fail if in fail queue

    trapum1.create_new_dataproduct(...) # Give reference to parent_id of processed file 
