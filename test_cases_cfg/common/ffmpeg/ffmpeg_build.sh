build_ffmpeg() {    
    set -e
        SrcPath=${BENCH_PATH}"443.ffmpeg"
        BuildPATH="$CALIPER_TMP/build.ffmpeg"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
   myOBJPATH=${INSTALL_DIR}/bin

   rm -rf $BuildPATH
        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
        then
      mkdir -p $BuildPATH
      pushd $BuildPATH
      $TOP_SRCDIR/configure --disable-yasm  --target-os=linux  --enable-demuxers --enable-decoders --enable-decoder=flac --disable-stripping --disable-ffserver --disable-ffprobe --enable-muxer=spdif --disable-devices --enable-parsers --disable-bsfs --disable-protocols --enable-protocol=file   --disable-postproc --disable-logging     
      make     
      $STRIP ffmpeg     
      cp    ffmpeg  $myOBJPATH/
           popd
      rm -rf $BuildPATH
        fi

        if [ $ARCH = "arm_32" ]
   then
                mkdir -p $BuildPATH
                pushd $BuildPATH
      $TOP_SRCDIR/configure --disable-yasm  --target-os=linux --arch=arm --enable-demuxers --enable-decoders --enable-decoder=flac --disable-stripping --enable-ffmpeg --disable-ffplay --disable-ffserver --disable-ffprobe --disable-encoders --disable-muxers --enable-muxer=spdif --disable-devices --enable-parsers --disable-bsfs --disable-protocols --enable-protocol=file --disable-protocol=http --disable-protocol=https --disable-protocol=udp --disable-filters --disable-avdevice --enable-cross-compile --cross-prefix=${ARMCROSS}-  --disable-neon --disable-postproc --disable-logging --extra-cflags="-mfpu=vfpv4 "     
                make     
                $STRIP ffmpeg     
                cp    ffmpeg  $myOBJPATH/
                popd
                rm -rf $BuildPATH
   fi
}

build_ffmpeg

