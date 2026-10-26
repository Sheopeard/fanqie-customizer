package io.github.mianxyz.fanqiecustomizer;

public final class TargetVersionTest {
    public static void main(String[] args){
        check(TargetVersion.supports(74132L,"7.4.1.32"),"exact supported build");
        check(!TargetVersion.supports(73932L,"7.3.9.32"),"old mappings cannot share new rules");
        check(!TargetVersion.supports(74133L,"7.4.1.32"),"same name with another code rejected");
        check(!TargetVersion.supports(74132L,"7.4.1.33"),"same code with another name rejected");
        check(!TargetVersion.supports(74132L,null),"missing version name rejected");
        System.out.println("TargetVersionTest passed");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
