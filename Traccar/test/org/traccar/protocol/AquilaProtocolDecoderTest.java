package org.traccar.protocol;

import org.junit.Test;
import org.traccar.ProtocolTest;

public class AquilaProtocolDecoderTest extends ProtocolTest {

    @Test
    public void testDecodeA() throws Exception {

        AquilaProtocolDecoder decoder = new AquilaProtocolDecoder(null);

        verifyPosition(decoder, text(
                "$$CLIENT_1ZF,170215089,20,18.462809,73.824188,170613182744,A,01,123456,*37"));

        verifyPosition(decoder, text(
                "$$CLIENT_1ZF,170215089,1,18.462809,73.824188,170613182744,A,19,0,0,256,4,4.860000,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,259,3731,*37"));

        verifyPosition(decoder, text(
                "$$CLIENT_1ZF,170222318,101,22.846016,75.949104,170321103506,A,0,0,244991,0,10,0.860000,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,12483,294,*3D"));

        verifyNull(decoder, text(
                "$$CLIENT_1ZF,170222318,15,2_00AP,70.35.195.185,5089,internet,T1:10 S,T2:1 M,Ad1:9164061023,Ad2:9164061023,TOF:0 S,,OSC:75 KM,OST:0 S,GPS:YES,Ignition:ON,*75"));

        verifyPosition(decoder, text(
                "$$CLIENT_1ZF,170222318,1,22.836912,75.942215,170321110736,A,11,12,247196,103,10,0.810000,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,13325,306,*36"));

        verifyPosition(decoder, text(
                "$$CLIENT_1ZF,130329214,1,12.962985,77.576484,140127165433,A,22,0,0,140,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1253,420,1,0,1,0,0,1,P(01:410104000102|05:410521|0C:410C0000|0D:410D65|21:4121161C),D(P0121|B2105),-895,745,-145,300,*26"));

        verifyPosition(decoder, text(
                "$$CLIENT_1NS,101010119,1,22.845943,75.949059,170202184000,A,27,0,0,120,31141,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,399,3709,0,0,0,0,0,0,P(01:|04:|05:|0B:|0C:|0D:|10:|1C:|21:|23:|30:|31:|1F:|11:|00:|00:|),D(),-89,44,-1062,0,*49"));

        verifyPosition(decoder, text(
                "$$CLIENT_1DT,151028368,1,19.108438,72.925308,160628154920,A,22,0,0,131,3503,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,*1D"));

        verifyNull(decoder, text(
                "$$CLIENT_1DT,160319372,1,28.549541,77.249802,160628140743,A,23,0,-65025,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,*0D"));

        verifyPosition(decoder, text(
                "$$SRINI_1MS,141214807,1,12.963515,77.533844,150925161628,A,27,0,8,0,68,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,*43"));

        verifyPosition(decoder, text(
                "$$CLIENT_1ZF,130329214,1,12.962985,77.576484,140127165433,A,22,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,*26"));

        verifyPosition(decoder, text(
                "$$CLIENT_1WP,141216511,3,12.963123,77.534012,150908163534,A,31,0,0,0,7,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,*28"));

        verifyPosition(decoder, text(
                "$$CLIENT_1WP,141216511,3,12.963212,77.533989,150908164041,V,31,0,0,0,8,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,*2A"));

    }

    @Test
    public void testDecodeB() throws Exception {

        AquilaProtocolDecoder decoder = new AquilaProtocolDecoder(null);

        verifyPosition(decoder, text(
                "$Header,nliven,EMR,861693034634154,NM,09112017155133,A,12.976495,N,77.549713,E,906.0,0.0,23,G,KA01I2000,+919844098440*4B"));

        verifyPosition(decoder, text(
                "$EPB,iTriangle1,EMR,864495034445822,SP,03082018110730,A,22.829292,N,75.935806,E,543.0,0.0,0,G,KA01G1234,+9164061023*13"));

        verifyPosition(decoder, text(
                "$Header,iTriangle,1_37T02B0164MAIS_2,NR,1,L,864495034490141,KA01I2000,1,19042018,102926,22.846401,N,75.948952,E,0.0,311,5,578.0,3.80,3.67,AirTel,0,1,12.5,4.3,1,C,14,404,93,0456,16db,29,ebd8,0458,28,3843,18ab,25,072e,18ab,22,35da,0458,0000,00,031181,0.0,0.0,0,()*34"));

        verifyPosition(decoder, text(
                "$Header,nliven,1_37T02B0164MAIS,BR,6,L,861693034634154,KA01I2000,1,09112017,160702,12.976593,N,77.549782,E,25.1,344,15,911.0,1.04,0.68,Airtel,1,1,11.8,3.8,1,C,24,404,45,61b4,9ad9,31,9adb,61b4,35,ffff,0000,33,ffff,0000,31,ffff,0000,0001,00,000014,0.0,0.1,4,()*1E"));

        verifyPosition(decoder, text(
                "$Header,iTriangle,1_37T02B0164MAIS_2,NR,1,L,864495034490141,KA01I2000,1,31032018,122247,22.845999,N,75.949005,E,0.0,44,16,545.0,1.19,0.65,AirTel,1,1,12.0,4.3,0,C,13,404,93,0456,16db,27,16dd,0456,22,3843,18ab,19,ebd8,0458,14,072c,18ab,0101,00,003735,0.0,0.0,0,()*48"));

        verifyNull(decoder, text(
                "$Header,nliven,KA01I2000,861693034634154,1_37T02B0164MAIS,AIS140,12.976545,N,77.549759,E*50"));

    }

}
