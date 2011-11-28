require 'thread'

# For a music dir structure of Artist/Album/*.flac, this will recreate
# that structure, rooted under some other dir, and encode the flac
# files to oggs in the new directory. It also copies any .jpg files it
# finds. It runs as many concurrent processes as the number given on
# the command line.

class TaskQueue
  def initialize
    @cmds = Queue.new
    @lock = Mutex.new
  end
  
  def <<(cmd)
    @cmds << cmd
  end

  def size
    @cmds.size
  end

  def take
    @lock.synchronize do
      if @cmds.empty?
        :done
      else
        @cmds.pop
      end
    end
  end
end

class Worker
  def initialize(tasks)
    @tasks = tasks
  end
  
  def start
    Thread.new do
      done = false
      until done
        cmd = @tasks.take
        if cmd == :done
          done = true
        else
          puts "#{self.inspect} [#{cmd}]"
          run_cmd(cmd)
        end
      end
    end
  end

  def run_cmd(cmd)
    io = IO.popen(cmd)
    io.readlines
  end
end

class TaskMan
  def initialize(max_jobs)
    @tasks = TaskQueue.new
    @workers = []
    max_jobs.times {@workers << Worker.new(@tasks)}
  end
  
  def <<(cmd)
    @tasks << cmd
  end
  
  def start
    puts "Running #{@tasks.size} jobs"
    threads = @workers.map {|s| s.start}
    threads.each {|t| t.join}
  end
end

class OggEncodeCommand
  def initialize(file, dest_dir)
    @flac_file = file
    ogg_file = File.join(dest_dir, file.gsub(/\.flac/, '.ogg'))
    ogg_file_dir = File.dirname(ogg_file)
    @cmd = "oggenc -Q -q 8 -o '#{ogg_file}' '#{file}'"
  end
  
  attr_reader :cmd
end

class Mp3EncodeCommand
  def initialize(file, dest_dir)
    mp3_file = File.join(dest_dir, file.gsub(/\.flac/, '.mp3'))
    mp3_file_dir = File.dirname(mp3_file)
    @cmd = "mkdir -p '#{mp3_file_dir}' && flac --silent -d -c '#{file}' | lame --preset standard --silent - '#{mp3_file}'"
  end
  
  attr_reader :cmd
end

def usage
  puts "Usage: "
  puts "#$0 <encoder> <maxjobs> <dest_dir> <src_dir>+"
  puts "   where <encoder> is either ogg or mp3."
end

if __FILE__ == $0
  if ARGV.size < 4
    usage
    exit 1
  end
  
  encoder_class = OggEncodeCommand
  if ARGV.shift == 'mp3'
    encoder_class = Mp3EncodeCommand
  end

  max_jobs = ARGV.shift.to_i
  taskman = TaskMan.new(max_jobs)
  dest_dir = ARGV.shift

  ARGV.each do |src_dir|
    Dir[File.join(src_dir, '*.flac')].entries.each do |file|
      taskman << encoder_class.new(file, dest_dir).cmd
    end
    
    Dir[File.join(src_dir, '*.jpg')].entries.each do |file|
      dir = File.join(dest_dir, File.dirname(file))
      taskman << "mkdir -p '#{dir}' && cp '#{file}' '#{dir}'"
    end
  end

  taskman.start
  puts 'done'
end