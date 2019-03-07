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
            last_id =  int(self.cursor.lastrowid)
            return last_id
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
    __NAME = "trapum_06mar19"
    __USER = "root"
    __PASSWD = "Praj3108!"
    def __init__(self):
        super(TrapumDataBase,self).__init__()

    def connect(self):
        return MySQLdb.connect(
            host=self.__HOST,
            db=self.__NAME,
            user=self.__USER,
            passwd=self.__PASSWD)


     #Before Observations
    def create_project(self,name,notes):
        """
        @brief   Creates a new project entry in Projects table     

        @params  Name    Name of the project             
        @params  notes   any extra information for the project 
        """ 
        cols=["name","notes"]
        values = ["'%s'"%name,"'%s'"%notes]
        last_id = self.simple_insert("Projects",cols,values)
        return last_id 

    def create_beamformer_config(self,centre_freq,bandwidth,nchans,tsamp,receiver,metadata):
        """
        @brief   Creates a new beamformer configuration entry in the Beamformer Configurations table  

        @params  centre_freq    Observation frequency in MHz 
        @params  bandwidth             Bandwidth used in MHz
        @params  nchans         Number of channels
        @params  tsamp          Sampling time in us
        @params  receiver       Receiver used
        @params  metadata       Info on other parameters as a key,value pair
        """ 
        cols=["`centre_frequency`","`bandwidth`","`nchans`","`tsamp`","`receiver`","`metadata`"]
        values = ["'%f'"%centre_freq,"'%f'"%bandwidth,"'%d'"%nchans,"'%f'"%tsamp,"%s"%receiver,"'%s'"%metadata]
        last_id = self.simple_insert("Beamformer_Configuration",cols,values)
        return last_id


    def create_target(self,project_id,source_name,ra,dec,region,semi_major_axis,semi_minor_axis,position_angle,metadata,notes):
        """
        @brief   Creates a target entry in Targets table

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
        values = ["%d"%project_id,"%s"%source_name,"%s"%ra,"%s"%dec,"%s"%region,"%s"%semi_major_axis,"%s"%semi_minor_axis,
                  "%s"%position_angle,"%s"%metadata,"%s"%notes]
        last_id = self.simple_insert("Targets",cols,values)
        return last_id

    # During Observations
    def create_pointing(self,target_id,bf_config_id,tobs,utc_start,sb_id,metadata,notes):
        """
        @brief   Creates a pointing entry in Pointings table     

        @params  target_id    Unique target identifier
        @params  bf_config_id Unique configuration identifier
        @params  tobs         Length of observation (in seconds) 
        @params  utc_start    UTC start time of observation HH:MM:SS
        @params  sb_id        Unique schedule block identifier
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """ 
         
        cols = ["`target_id`","`bf_config_id`","`tobs`","`utc_start`","`sb_id`","`metadata`","`notes`"]     
        vals = ["%d"%target_id,"%d"%bf_config_id,"%f"%tobs,"'%s'"%utc_start,"'%s'"%sb_id,"'%s'"%metadata,"'%s'"%notes]
        last_id = self.simple_insert("Pointings",cols,vals)
        return last_id
         

    # After observations
    
    def create_beam(self,pointing_id,on_target,ra,dec,coherent):
        """
        @brief   Creates a Beam entry in Beams table     

        @params  pointing_id   Unique pointing identifer for beam             
        @params  on_target     indicates if beam is on or off target: 1 for on 0 for off
        @params  ra            Right Ascension in HH::MM::SS of beam
        @params  dec           Declination in DD::MM::SS of beam
        @params  coherent  indicates if beam is coherent or incoherent: 1 for coherent on 0 for incoherent
        """ 
        cols = ["`pointing_id`","`on_target`","`ra`","`dec`","`coherent`"]
        vals = ["%d"%pointing_id,"%d"%on_target,"%f"%ra,"%f"%dec,"%d"%coherent]
        last_id = self.simple_insert("Beams",cols,vals)
        return last_id


    def update_tobs(self,pointing_id,tobs):
        """
        @brief   Update length of observation in Pointings table

        @params  pointing_id    Unique pointing identifer 
        @params  tobs           value of observation time
        """ 
        cols = "tobs"
        values = tobs
        condition = "pointing_id = %d"%pointing_id # update tobs for particular pointing id 
        last_id = self.simple_update("Pointings",cols,values,condition)
        return last_id


    def create_raw_dataproduct(self,pointing_id,beam_id,file_status,filepath,file_type,metadata,notes):
        """
        @brief   Create raw data product entry in Data_Products table, processing_id is NULL by default

        @params  pointing_id    Unique pointing identifer 
        @params  beam_id        Unique Beam identifier
        @params  file_status    If file exists or not: 1 if exists, 0 if deleted,  
        @params  filepath       Path to file
        @params  file_type      Type of file produced 
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """ 
        cols=["pointing_id","beam_id","file_status","filepath","file_type","metadata","notes"]
        values=["%d"%pointing_id,"%d"%beam_id,"'%s'"%file_status,"'%s'"%filepath,"'%s'"%file_type,"'%s'"%metadata,"'%s'"%notes]
        last_id = self.simple_insert("Data_Products",cols,values)
        return last_id
        
        
    def create_secondary_dataproduct(self,pointing_id,beam_id,processing_id,file_status,filepath,file_type,metadata,notes):
        """
        @brief   Create data product entry in Data_Products table

        @params  pointing_id    Unique pointing identifer 
        @params  beam_id        Unique Beam identifier
        @params  processing_id  Unique processing identifier,NULL if recorded from observation
        @params  file_status    If file exists or not: 1 if exists, 0 if deleted,  
        @params  filepath       Path to file
        @params  file_type      Type of file produced 
        @params  metadata       Info on other parameters as key value pair
        @params  notes          Any extra info about the target
        """ 
        cols=["pointing_id","beam_id","processing_id","file_status","filepath","file_type","metadata","notes"]
        values=["%d"%pointing_id,"%d"%beam_id,"%d"%processing_id,"'%s'"%file_status,"'%s'"%filepath,"'%s'"%file_type,"'%s'"%metadata,"'%s'"%notes]
        last_id = self.simple_insert("Data_Products",cols,values)
        return last_id

    def create_processing(self,pointing_id,pipeline_id,hardware_id,submit_time,start_time,end_time,process_status,metadata,notes):
        """
        @brief   Create a processing entry in Processings table
        
        @params  pointing_id    Unique pointing identifer 
        @params  pipeline_id    Unique pipeline identifer 
        @params  hardware_id    Unique hardware identifer 
        @params  submit_time    time of submitting job to queue (YYYY-MM-DD HH:MM:SS)
        @params  start_time     Start time of processing (YYYY-MM-DD HH:MM:SS)
        @params  end_time       End time of processing (YYYY-MM-DD HH:MM:SS)
        @params  process_status Status of the process. Options are : 0->submitted, 1->processing, 2->completed
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """ 
        cols = ["pointing_id","pipeline_id","hardware_id","submit_time","start_time","end_time"
                ,"process_status","metadata","notes"]
        vals=["%d"%pointing_id,"%d"%pipeline_id,"%d"%hardware_id,"'%s'"%submit_time,"'%s'"%start_time,"'%s'"%end_time,
              "'%s'"%process_status,"'%s'"%metadata,"'%s'"%notes]
        last_id = self.simple_insert("Processings",cols,vals)
        return last_id

    def update_submit_time(self,submit_time,processing_id):
        """
        @brief Update the time of job submission to queue

        @params value of submission time (YYYY-MM-DD HH:MM:SS)  
        """
        cols = ["submit_time"]
        values=["%s"%start_time]
        condition = "processing_id=%d"%processing_id
        self.simple_update("Processings",cols,values,condition)
       

    def update_process_status(self,process_status,processing_id):
        """
        @brief Update the status of a particular processing.Options are : 0->submitted, 1->processing, 2->completed

        @params Value indicating status
        """
        cols = ["process_status"]
        values=["%s"%process_status]
        condition = "processing_id=%d"%processing_id
        self.simple_update("Processings",cols,values,condition)


  
   # When pipeline starts
    def create_pipeline(self,HASH,name,notes):
        """
        @brief   Creates a pipeline entry in Pipelines table     

        @params  HASH    unique hash of pipeline                 
        @params  name    unique name of pipeline e.g. presto,peasoup                 
        @params  notes   any extra information for the project 
        """ 
        cols = ["hash","name","notes"]
        values = ["%s"%HASH,"%s"%name,"%s"%notes]
        last_id = self.simple_insert("Pipelines",cols,values)
        return last_id
    
    def create_pivot(self,dp_id,processing_id):
        """
        @brief   Creates a pivot entry in Processing_Pivot table     

        @params  dp_id          Unique dataproducts identifier 
        @params  processing_id  unique Processings identifier                
        """ 
        cols = ["dp_id","processing_id",]
        values = ["%s"%dp_id,"%s"%processing_id]
        last_id = self.simple_insert("Processing_Pivot",cols,values)
        return last_id
        

    def update_start_time(self,start_time,processing_id):
        cols = ["start_time"]
        values=["%s"%start_time]
        condition = "processing_id=%d"%processing_id 
        self.simple_update("Processings",cols,values)
        
   
    def create_hardware_config(self,name,metadata,notes):
        """
        @brief   Creates a hardware configuration in Hardwares table  
    
        @params  name         Name of hardware device 
        @params  metadata     Info on other parameters as key value pair
        @params  notes        Any extra info about the target
        """
        cols = ["name","metadata","notes"]
        values = ["'%s'"%name,"'%s'"%metadata,"'%s'"%notes]
        last_id = self.simple_insert("Hardwares",cols,values)
        return last_id

    
    # End of pipeline run 
    
   
    def update_end_time(self,end_time,processing_id):
        cols = ["end_time"]
        values = ["%s"%end_time]
        condition = "processing_id=%d"%processing_id 
        self.simple_update("Processings",cols,vals,condition)
    

    def get_obs_id_from_utc(self,utc):
        obs = qb.Table("Observations")
        select = obs.select(obs.obs_id)
        select.where = (obs.utc_start == utc)
        query,args = tuple(select)
        return query%args
   

    def get_project_id(self,description):
        condition = "name LIKE '%s'" % description
        return self.get_single_value("Projects","project_id",condition)
 
    def get_beams_for_pointing(self,pointing_id):
        condition = "pointing_id='%d'" %pointing_id
        return self.get_single_value("Beams","beam_id",condition)


  
    def update_file_status(self,file_status,dp_id):
        cols = ["file_status"]
        values = ["%d" %file_status]
        condition = "dp_id=%d"%dp_id
        self.simple_update("Data_Products",cols,values,condition)

 
    def simple_insert(self,table,cols,values):
        """
        @brief   Inserts new entry into respective table   
    
        @params  table        Table for new entry
        @params  cols         Columns in table to be changed
        @params  values       values for the respective columns to be added
  
        @return  lastrowid    last inserted primary key id
        """
        columns = str(tuple(cols)).replace('\'','')
        vals = str(tuple(values)).replace('\"','')
        print columns
        print vals
        print "INSERT INTO %s%s VALUES %s"%(table,columns,vals) 
        self.execute_insert("INSERT INTO %s%s VALUES %s"%(table,columns,vals)) 
        return self.cursor.lastrowid

    def simple_update(self,table,cols,values,condition):
        """
        @brief   Updates existing entry in respective table   
    
        @params  table        Table to update
        @params  cols         Columns in table to be updated
        @params  values       values for the respective columns to be updated
        """
        self.execute_insert("UPDATE %s set %s=%s WHERE %s"%(table,cols,values,condition))
        print "UPDATE %s set %s=%s WHERE %s"%(table,cols,values,condition)
        
    def get_values(self,table,col,condition):
        """
        @brief   Updates existing entry in respective table   
    
        @params  table        Table to analyse
        @params  cols         Columns in table to be checked
        @params  values       values for the respective columns to be retrieved

        @return  list of values requested
        """ 
        self.execute_query("select %s from %s where %s"%(col,table,condition))
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
    #trapum.execute_query('set @update_id:=0') # initiates latest updated primary key id to zero

    ####  Preparation for observation ####

    ##Targets and Projects will already be filled
    
    ## Create new subarray
#    trapum1.create_new_beamformer_config() #args to be filled
#
#    #### Observatiion has begun ####
#
#    ## Create_new_pointing
#    trapum1.create_new_pointing(..)
#
#    ## Create new Beams
#    trapum.create_new_beam(..)
#
#    ###### Observation has ended #########
#
#    ## Update tobs 
#    trapum1.update_tobs(current_time,condition) # Trigger that observation is over (how?) and how to get timestamp for tobs (time.strftime) ?
#
#    ##### Create new dataproduct #######
#    trapum1.create_new_dp_id(..) # processing_id =NULL,file_status= to be processed, filetype and path from obs table 
#
#    ######create new processing_id
#    trapum1.create_new_processing_id(..)  # processing_id=NULL, rest retrievable .. Assume that pipeline and hardware already available in tables(?)
#
#    #### Update submit time
#    trapum1.update_submit_time(...) # Trigger once job details (file path etc etc) submitted to rabbitmq
#
#    #trapum1.create_new_hardware_config_id ## How to get hardware details
#    trapum1.create_new_hardware_config
#
#    ### Update process status
#
#    trapum1.update_process_status('submitted')
#
#    ## Start of pipeline -- once consumed from rabbitmq
#
#    trapum1.create_new_pipeline_id(...)
#
#    trapum1.update_start_time (..) # Timestamps?
#
#    trapum1.update_process_status('running')
#    #
#
#    ## End of pipeline run
#
#    trapum1.update_end_time(..)   # Timestamps?
#
#    trapum1.update_process_status('completed and success/fail') # Update success if in success queue, or fail if in fail queue
#
#    #trapum1.update_file_status('processed') 
#
#    trapum1.create_new_dp_id(...) # Give reference to parent_id of processed file 


    # General problems..
    #   1. DEFAULT NULL   vs NOT NULL
    #   2. 



     

     
        

      
    
        


