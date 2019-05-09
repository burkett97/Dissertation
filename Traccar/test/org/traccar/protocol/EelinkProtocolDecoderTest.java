package org.traccar.protocol;

import org.junit.Test;
import org.traccar.ProtocolTest;
import org.traccar.model.Position;

public class EelinkProtocolDecoderTest extends ProtocolTest {

    @Test
    public void testDecode() throws Exception {

        EelinkProtocolDecoder decoder = new EelinkProtocolDecoder(null);

        verifyNull(decoder, binary(
                "454C0027E753035254407167747167670100180002035254407167747100200205020500010432000086BD"));

        verifyAttribute(decoder, binary(
                "676712003400e45c5b0ade02012e03702d87064546aa24066a1086018a0000002dc1a0ffffffff0afd074d000000000000000000000000fce0"),
                Position.PREFIX_TEMP + 2, -50.0);

        verifyAttribute(decoder, binary(
                "6767120043000e5c37387c0304e4e1b4f8194fa800160013009408012e03702d8706453c6e5b066f115f05710000001b067f8d248d240313020500000000000000000000000001cc"),
                Position.PREFIX_TEMP + 2, 28.75);

        verifyPosition(decoder, binary(
                "676714002414B05AD43A7D03026B92B10C395499FFD7000000000701CC00002495000014203604067B"));

        verifyNotNull(decoder, binary(
                "676714004F14B0E68CAFE58AA8E68AA5E8ADA621E5B9BFE4B89CE79C81E6B7B1E59CB3E5B882E58D97E5B1B1E58CBAE696B0E8A5BFE8B7AF3138EFBC88E8B79DE5AE87E998B3E5A4A7E58EA63230E7B1B3EFBC89"));

        verifyPosition(decoder, binary(
                "676780005a000001000000004c61743a4e33312e38333935352c4c6f6e3a5738322e36313334362c436f757273653a302e30302c53706565643a302e30306b6d2f682c4461746554696d653a323031372d31322d30322031313a32393a3433"));

        verifyPosition(decoder, binary(
                "676780005E5788014C754C754C61743A4E32332E3131313734330A4C6F6E3A453131342E3430393233380A436F757273653A302E30300A53706565643A302E31374B4D2F480A446174652054696D653A323031352D30392D31332032303A32313A3230"));

        verifyPosition(decoder, binary(
                "454C0050EAE2035254407167747167671200410021590BD93803026B940D0C3952AD0021000000000501CC0001A53F0170F0AB1305890F11000000000000C2D0001C001600000000000000000000000000000000"));

        verifyNull(decoder, binary(
                "676701000c007b03525440717505180104"));

        verifyPosition(decoder, binary(
                "6767120048000559c1829213059a7400008e277d000c000000000800cc00080d2a000034df3cf0b429dd82cad3048910320000000000007b7320d005ba0000000019a000000000000000000000"));

        verifyPosition(decoder, binary(
                "6767050020213b59c6aecdff41dce70b8b977d00000001fe000a36e30078fe010159c6aecd"));

        verifyPosition(decoder, binary(
                "676705002102b459ae7388fcd360d7034332b1000000028f000a4f64002eb101010159ae7388"));

        verifyPosition(decoder, binary(
                "676702001c02b259ae7387fcd360d6034332b2000000028f000a4f64002eb10101"));

        verifyPosition(decoder, binary(
                "6767050022001F59643640000000000000000000000001CC0000249500142000015964A6C0006E"));

        verifyAttributes(decoder, binary(
                "67670300040021006E"));

        verifyPosition(decoder, binary(
                "676705002200255964369D000000000000000000000001CC0000249500142000025964A71D006A"));

        verifyAttributes(decoder, binary(
                "67670300040028006A"));

        verifyPosition(decoder, binary(
                "676712002d066c592cca6803002631a60b22127700240046005c08020d000301af000da0fd12007f11ce05820000001899c0"));

        verifyPosition(decoder, binary(
                "676702002509f65868507603a1e92e03cf90fe000000019f000117ee00111e0120631145003101510000"));

        verifyAttributes(decoder, binary(
                "676712001e0092579714d60201f90001785003a301cd1a006a118504f2000000000000"));

        verifyPosition(decoder, binary(
                "676712003400505784cc0b130246479b07d05a06001800000000070195039f046100002cc52e6466b391604a4900890e7c00000000000006ca"));

        verifyPosition(decoder, binary(
                "676714002b00515784cc24130246479b07d05a06001800010000060195039f046100002cc52f6466b391604a49020089"));

        verifyNull(decoder, binary(
                "676701000c002603541880486128290120"));

        verifyPosition(decoder, binary(
                "676704001c01a4569ff2dd0517a0f7020b0d9a06011000d8001e005b0004450183"));

        verifyPosition(decoder, binary(
                "676705002200ba569fc3520517a0d8020b0f740f007100d8001e005b0004460101569fd162001f"));

        verifyPosition(decoder, binary(
                "676702002500bb569fc3610517a091020b116000001900d8001e005b00044601001f1170003200000000"));

        verifyPosition(decoder, binary(
                "676704001c00b7569fc3020517a2d7020b08e100000000d8001e005b0004460004"));

        verifyNull(decoder, binary(
                "676701000b001b035418804661834901"));

        verifyAttributes(decoder, binary(
                "6767030004001A0001"));

        verifyNull(decoder, binary(
                "6767070088001050E2281400FFFFFFFF02334455660333445566043344556605AA00000007334455660A334455660B334455660C4E2000000DAA0000000E334455660F3344556610AAAA000011334455661C334455661F334455662133445566423344556646334455664D334455665C334455665E33445566880000000089000000008A000000008B00000000"));

        verifyPosition(decoder, binary(
                "676702001b03c5538086df0190c1790b3482df0f0157020800013beb00342401"));

    }

}