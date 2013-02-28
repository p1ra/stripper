#!/usr/bin/python

import sys
import subprocess

errormap = {
    0:"File not found.",
    1:"'zip' tool not found.",
    2:"'unzip' tool not found.",
    3:"Unable to unzip target.",
    4:"Error running baksmali. Please check if framework path is correct.",
    5:"Error running smali.",
    6:"Unable to move classes.dex.",
    7:"Unable to zip Target.",
    8:"Unable to perform cleaning.",
    9:"Unable to move deodexed APK.",
    10:"'java' not found.",
    11:"Apktool was unable to decompile target.",
    12:"Unable to convert dex to jar.",
    13:"Unable to create 'src' directory.",
    14:"Unable to extract '.class' files.",
    15:"Unable to generate '.java' files.",
}

def error(num):
    global errormap

    print '[-] Error: %s' % errormap.get(num)
    sys.exit(0)

def run(command,error_num):
    try:
        subprocess.check_call([command],stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,shell=True)
    except:
        error(error_num)

def check_file(target_file):
    try:
        with open(target_file) as f: pass
    except:
        return False

    return True

def check_tools():
    run("zip -h",1)
    run("unzip -h",2)
    run("java -h",10)

def check_odex(target):
    run("unzip %s.apk -d %s" % (target,target),3)
    return not check_file("%s/classes.dex" % target)

def deodex(target,framework):
    if check_file(target + ".odex") == False:
        error(0)

    run("java -jar ./tools/baksmali.jar -a 17 -x %s.odex -d %s -o baksmali_out" % 
        (target,framework),4)
    run("java -jar ./tools/smali.jar -a 17 -o classes.dex baksmali_out",5)
    run("mv classes.dex %s" % target,6)
    run("cd %s && zip -r %s.deodex.apk ." % (target,target) ,7)
    run("mv %s/%s.deodex.apk ." % (target,target) ,9)

def decompile(target):
    run("java -jar ./tools/apktool.jar d -f %s.apk" % target,11)
    run("./tools/dex2jar/d2j-dex2jar.sh -f %s.apk" % target,12)
    run("mkdir %s/class/" % target,13)
    run("unzip %s-dex2jar.jar -d %s/class/" % (target,target),14)
    run("./tools/jad -o -r -sjava -d %s/src %s/class/**/*.class" %
        (target,target),15)    

def clean_up(target):
    run("rm -rf %s" % target,8)
    run("rm -rf baksmali_out",8)
    run("rm -rf *-dex2jar.jar",8)

def main():
    if len(sys.argv) < 2:
        print "Usage: %s target_apk [framework_dir]" % sys.argv[0]
        sys.exit(0)

    target = sys.argv[1].split(".")[0]

    print "[+] == Stripper v0.1 =="
    print "[+] Target = %s" % target

    check_tools()
    check_file(target+".apk")

    clean_up(target)

    odex = check_odex(target)

    if odex == True:
        print "[+] Odexed APK detected."
        print "[+] Deodexing target."

        framework = "./framework"
        if len(sys.argv) == 3:
            framework = sys.argv[2]

        print '[+] Using framework folder "%s"' % framework
        
        deodex(target,framework)
    else:
        print "[+] Deodexed APK detected."

    clean_up(target)
    
    if odex: target += ".deodex"

    print "[+] Decompiling Target."
    decompile(target)
    
    run("rm -rf *-dex2jar.jar",8)
    
    print "[+] Done."

if __name__ == "__main__":
    main()

