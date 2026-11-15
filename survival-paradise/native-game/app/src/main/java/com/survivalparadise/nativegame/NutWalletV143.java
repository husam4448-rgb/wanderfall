package com.survivalparadise.nativegame;

/** Exact integer arithmetic: 100 iron = 1 silver, 100 silver = 1 gold.
 * Money is a pocket wallet (not a backpack item or an old scrap alias).
 */
public final class NutWalletV143 {
    public static final long SILVER=100L,GOLD=10000L,MAX=1000000000L;
    public static final int IRON=0,SILVER_COIN=1,GOLD_COIN=2;
    public static final String[] NAMES={"Iron nuts","Silver nuts","Gold nuts"};
    private long total;
    public NutWalletV143(){this(0);}
    public NutWalletV143(long iron){if(iron<0||iron>MAX)throw new IllegalArgumentException();total=iron;}
    public long iron(){return total;}
    public int coins(int denomination){
        if(denomination==GOLD_COIN)return (int)(total/GOLD);
        if(denomination==SILVER_COIN)return (int)((total%GOLD)/SILVER);
        if(denomination==IRON)return (int)(total%SILVER);
        return 0;
    }
    public static long unit(int denomination){
        return denomination==IRON?1:denomination==SILVER_COIN?SILVER:
            denomination==GOLD_COIN?GOLD:0;
    }
    public boolean canCredit(long value){return value>0&&total<=MAX-value;}
    public boolean credit(long value){if(!canCredit(value))return false;total+=value;return true;}
    public boolean canDebit(long value){return value>0&&total>=value;}
    public boolean debit(long value){if(!canDebit(value))return false;total-=value;return true;}
    public long takeAll(){long n=total;total=0;return n;}
    public String encode(){return Long.toString(total);}
    public boolean decode(String encoded){
        try{
            long value=Long.parseLong(encoded);
            if(value<0||value>MAX)return false;
            total=value;return true;
        }catch(Exception ignored){return false;}
    }
    public String display(){
        return coins(GOLD_COIN)+" GOLD  •  "+coins(SILVER_COIN)+
            " SILVER  •  "+coins(IRON)+" IRON";
    }
    public static String price(long iron){
        if(iron<0)return "INVALID";
        return (iron/GOLD)+"g "+((iron%GOLD)/SILVER)+"s "+(iron%SILVER)+"i";
    }
}
