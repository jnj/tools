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
          puts cmd
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

class ShellEscaper
  def escape(s)
    return "''" if s.empty?
    s.gsub(/([^A-Za-z0-9_\-.,:\/@\n])/n, "\\\\\\1")
  end
end

class OggEncodeCommand
  def initialize(file, dest_dir)
    @se = ShellEscaper.new
    ogg_file = @se.escape(File.join(dest_dir, file.gsub(/\.flac/, '.ogg')))
    flac_file = @se.escape(file)
    @cmd = "oggenc -Q -q 8 -o #{ogg_file} #{flac_file}"
  end
  
  attr_reader :cmd

  def to_s
    cmd
  end
end

class Mp3EncodeCommand
  def initialize(file, dest_dir)
    @se = ShellEscaper.new
    @flacfile = @se.escape(file).force_encoding('UTF-8')
    tags_options = make_tags_options.force_encoding('UTF-8')
    @mp3_file = @se.escape(File.join(dest_dir, file.gsub(/\.flac/, '.mp3'))).force_encoding('UTF-8')
    @cmd = "flac --silent -d -c #{@flacfile} | lame -V 0 #{tags_options} --silent - #{@mp3_file}"
  end

  def make_tags_options
    tags = get_tags
    { 
      "ARTIST" => "ta",
      "ALBUM" => "tl",
      "GENRE" => "tg",
      "DATE" => "ty",
      "TITLE" => "tt",
      "TRACKNUMBER" => "tn"
    }.inject("") do |s, kvpair|
      tagname = kvpair[0]
      optionname = kvpair[1]
      r = ""
      if tags.include?(tagname)
        tagval = tags[tagname]
        r = "#{s} --#{optionname} #{tagval}"
      end
      r
    end
  end
  
  def get_tags  
    x = `metaflac --export-tags-to=- #{@flacfile}`
    taglines = x.lines
    taglines.inject({}) do |h, l|
      m = l.match('([A-Z]+)=(.+)')
      if m != nil
        h[m[1]] = @se.escape(m[2])
      end
      h
    end
  end

  attr_reader :cmd

  def to_s
    cmd
  end
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
    dir = File.join(dest_dir, src_dir)
    `mkdir -p '#{dir}'`
  end
  
  ARGV.each do |src_dir|
    Dir[File.join(src_dir, '*.flac')].entries.each do |file|
      taskman << encoder_class.new(file, dest_dir).cmd
    end
    
    Dir[File.join(src_dir, '*.jpg')].entries.each do |file|
      dir = File.join(dest_dir, File.dirname(file))
      taskman << "cp '#{file}' '#{dir}'"
    end
  end

  taskman.start
  puts 'done'
end
