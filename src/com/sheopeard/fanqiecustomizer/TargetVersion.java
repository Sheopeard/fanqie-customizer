package com.sheopeard.fanqiecustomizer;

/** Keep obfuscated 7.4.5.32 rules away from every other host build. */
final class TargetVersion {
    static final long CODE=74532L;
    static final String NAME="7.4.5.32";
    private TargetVersion(){}
    static boolean supports(long code,String name){return code==CODE&&NAME.equals(name);}
}
