package com.sheopeard.fanqiecustomizer;

public final class TargetVersionTest {
    public static void main(String[] args){
        check(TargetVersion.supports(74532L,"7.4.5.32"),"exact supported build");
        check(!TargetVersion.supports(74332L,"7.4.3.32"),"old mappings cannot share new rules");
        check(!TargetVersion.supports(74533L,"7.4.5.32"),"same name with another code rejected");
        check(!TargetVersion.supports(74532L,"7.4.5.33"),"same code with another name rejected");
        check(!TargetVersion.supports(74532L,null),"missing version name rejected");
        System.out.println("TargetVersionTest passed");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
