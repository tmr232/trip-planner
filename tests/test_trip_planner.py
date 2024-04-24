import pytest

from trip_planner.trip_planner import Coords, get_coords_from_url, parse_directions_url


@pytest.mark.parametrize(
    ("url", "coords"),
    [
        (
            "https://www.google.com/maps/place/Himeji+Castle/@34.8394534,134.6913298,17z/data=!3m1!4b1!4m6!3m5!1s0x3554e003a23324b3:0x7a4f8c2f6eba81b1!8m2!3d34.839449!4d134.6939047!16zL20vMDE4bmN4?entry=ttu",
            Coords(lon=134.6939047, lat=34.839449),
        ),
        (
            "https://www.google.com/maps/place/Universal+Studios+Japan/@34.6656812,135.4297436,17z/data=!3m1!4b1!4m6!3m5!1s0x6000e0d083d5e25d:0x3605fe25303252aa!8m2!3d34.6656768!4d135.4323185!16zL20vMDczN3g1?entry=ttu",
            Coords(lon=135.4323185, lat=34.6656768),
        ),
        (
            "https://www.google.com/maps/place/Osaka+Aquarium+Kaiyukan/@34.6545226,135.4263896,17z/data=!3m2!4b1!5s0x6000e8f48fa243ff:0x25fc1f29292f7889!4m6!3m5!1s0x6000e8f48c0da9cd:0x6f83c520ae082ccc!8m2!3d34.6545182!4d135.4289645!16zL20vMDJjeW13?entry=ttu",
            Coords(lon=135.4289645, lat=34.6545182),
        ),
        (
            "https://www.google.com/maps/place/Tateyama+Kurobe+Alpine+Route/@36.5832256,137.442958,17z/data=!3m1!4b1!4m6!3m5!1s0x5ff7e8b6792d22c3:0x5f89a4c762ddb1eb!8m2!3d36.5832213!4d137.4455329!16s%2Fg%2F11cmsz8wvs?entry=ttu",
            Coords(lon=137.4455329, lat=36.5832213),
        ),
        (
            "https://www.google.com/maps/place/Nara+Park/@34.6850514,135.8404371,17z/data=!3m1!4b1!4m6!3m5!1s0x60013996bd8c6061:0xf96cacf357447456!8m2!3d34.685047!4d135.843012!16s%2Fm%2F02pwmjl?entry=ttu",
            Coords(lon=135.843012, lat=34.685047),
        ),
        (
            "https://www.google.com/maps/place/DiverCity+Tokyo+Plaza/@35.6251856,139.7756314,17z/data=!3m1!5s0x601889f9d3afd357:0x4ceb5b057f39f5fb!4m14!1m7!3m6!1s0x601889f9d36ebaa5:0x67f4219bfa09db77!2sDiverCity+Tokyo+Plaza!8m2!3d35.6251856!4d139.7756314!16s%2Fg%2F1hbpwy50x!3m5!1s0x601889f9d36ebaa5:0x67f4219bfa09db77!8m2!3d35.6251856!4d139.7756314!16s%2Fg%2F1hbpwy50x?entry=ttu",
            Coords(lon=139.7756314, lat=35.6251856),
        ),
        (
            "https://www.google.com/maps/place/Ghibli+Museum/@35.696238,139.5704317,17z/data=!3m1!4b1!4m6!3m5!1s0x6018ee34e5038c2d:0x4de155903f849205!8m2!3d35.696238!4d139.5704317!16zL20vMDY5MDY0?entry=ttu",
            Coords(lon=139.5704317, lat=35.696238),
        ),
        (
            "https://www.google.com/maps/place/Toei+Animation+Museum/@35.7522416,139.5945011,17z/data=!3m1!4b1!4m6!3m5!1s0x6018efc3552c8307:0xee5f969e1ad151ac!8m2!3d35.7522416!4d139.5945011!16s%2Fg%2F11b635jqds?entry=ttu",
            Coords(lon=139.5945011, lat=35.7522416),
        ),
        (
            "https://www.google.com/maps/place/Itsukushima/@34.2714518,132.2642232,13z/data=!3m1!4b1!4m6!3m5!1s0x355ab6cf888dc919:0xc91f62ebee004301!8m2!3d34.2732114!4d132.3052488!16zL20vMDQzMXds?entry=ttu",
            Coords(lon=132.3052488, lat=34.2732114),
        ),
        (
            "https://www.google.com/maps/place/Fushimi+Inari+Taisha/@34.9676989,135.7766127,17z/data=!3m1!4b1!4m6!3m5!1s0x60010f153d2e6d21:0x7b1aca1c753ae2e9!8m2!3d34.9676945!4d135.7791876!16zL20vMDVsZHJt?entry=ttu",
            Coords(lon=135.7791876, lat=34.9676945),
        ),
        (
            "https://www.google.com/maps/place/Nikk%C5%8D+T%C5%8Dshog%C5%AB/@36.7580921,139.5961717,17z/data=!3m1!4b1!4m6!3m5!1s0x601fa6c553212035:0xab505b717af00e94!8m2!3d36.7580878!4d139.5987466!16zL20vMDQ3ZzAx?entry=ttu",
            Coords(lon=139.5987466, lat=36.7580878),
        ),
        (
            "https://www.google.com/maps/place/Shinagawa+Aquarium/@35.5884803,139.7326298,17z/data=!3m1!4b1!4m6!3m5!1s0x601861ce9e9808b3:0xed2d89a0c1fc82c0!8m2!3d35.588476!4d139.7375007!16s%2Fm%2F0nbdm0v?entry=ttu",
            Coords(lon=139.7375007, lat=35.588476),
        ),
        (
            "https://www.google.com/maps/place/Magome,+Nakatsugawa,+Gifu+508-0502,+Japan/@35.5283395,137.5642841,15z/data=!3m1!4b1!4m6!3m5!1s0x601cb71add823007:0x7d766e65361116fa!8m2!3d35.5315174!4d137.5717516!16zL20vMDM4ZDhx?entry=ttu",
            Coords(lon=137.5717516, lat=35.5315174),
        ),
        (
            "https://www.google.com/maps/place/Tsumago-juku/@35.5794325,137.5938093,18z/data=!4m6!3m5!1s0x601cb7e4a598bb33:0x87bc2c35315036f6!8m2!3d35.5775876!4d137.5956667!16zL20vMDkweXd6?entry=ttu",
            Coords(lon=137.5956667, lat=35.5775876),
        ),
        (
            "https://www.google.com/maps/place/Senj%C5%8Dgahara+Grassy+Plain./@36.7772522,139.4417249,17z/data=!3m1!4b1!4m6!3m5!1s0x601fade731eda30d:0x99aa84da309ebfaf!8m2!3d36.7772479!4d139.4442998!16zL20vMDkxc2tt?entry=ttu",
            Coords(lon=139.4442998, lat=36.7772479),
        ),
        (
            "https://www.google.com/maps/place/Kanazawa,+Ishikawa,+Japan/@36.5061033,136.6871625,11z/data=!3m1!4b1!4m6!3m5!1s0x5ff83655468566c3:0x8df155c46fde6215!8m2!3d36.5597341!4d136.6520375!16zL20vMGdwNXFs?entry=ttu",
            Coords(lon=136.6520375, lat=36.5597341),
        ),
        (
            "https://www.google.com/maps/place/Kenroku-en/@36.5621321,136.6600766,17z/data=!3m1!4b1!4m6!3m5!1s0x5ff83383f9b25905:0x970a7b3df003f2e4!8m2!3d36.5621278!4d136.6626515!16zL20vMDJsNnZ4?entry=ttu",
            Coords(lon=136.6626515, lat=36.5621278),
        ),
        (
            "https://www.google.com/maps/place/Takayama,+Gifu,+Japan/@36.1454132,137.0386522,11z/data=!3m1!4b1!4m6!3m5!1s0x6002a342a14fc349:0xd4f2fb84f0b8e3dc!8m2!3d36.1461317!4d137.252159!16zL20vMDF3bDEz?entry=ttu",
            Coords(lon=137.252159, lat=36.1461317),
        ),
        (
            "https://www.google.com/maps/place/Akihabara,+Taito+City,+Tokyo+110-0006,+Japan/@35.7021768,139.7719771,17z/data=!3m1!4b1!4m6!3m5!1s0x60188ea73ea6f4ff:0x5eb9f1e50fe061e3!8m2!3d35.7022589!4d139.7744733!16s%2Fg%2F11bc6tf5hn?entry=ttu",
            Coords(lon=139.7744733, lat=35.7022589),
        ),
        (
            "https://www.google.com/maps/place/Himeji+Castle/@34.8394534,134.6913298,17z/data=!3m1!4b1!4m6!3m5!1s0x3554e003a23324b3:0x7a4f8c2f6eba81b1!8m2!3d34.839449!4d134.6939047!16zL20vMDE4bmN4?entry=ttu",
            Coords(lon=134.6939047, lat=34.839449),
        ),
        (
            "https://www.google.com/maps/place/Universal+Studios+Japan/@34.6656812,135.4297436,17z/data=!3m1!4b1!4m6!3m5!1s0x6000e0d083d5e25d:0x3605fe25303252aa!8m2!3d34.6656768!4d135.4323185!16zL20vMDczN3g1?entry=ttu",
            Coords(lon=135.4323185, lat=34.6656768),
        ),
        (
            "https://www.google.com/maps/place/Osaka+Aquarium+Kaiyukan/@34.6545226,135.4263896,17z/data=!3m2!4b1!5s0x6000e8f48fa243ff:0x25fc1f29292f7889!4m6!3m5!1s0x6000e8f48c0da9cd:0x6f83c520ae082ccc!8m2!3d34.6545182!4d135.4289645!16zL20vMDJjeW13?entry=ttu",
            Coords(lon=135.4289645, lat=34.6545182),
        ),
        (
            "https://www.google.com/maps/place/Tateyama+Kurobe+Alpine+Route/@36.5832256,137.442958,17z/data=!3m1!4b1!4m6!3m5!1s0x5ff7e8b6792d22c3:0x5f89a4c762ddb1eb!8m2!3d36.5832213!4d137.4455329!16s%2Fg%2F11cmsz8wvs?entry=ttu",
            Coords(lon=137.4455329, lat=36.5832213),
        ),
        (
            "https://www.google.com/maps/place/Nara+Park/@34.6850514,135.8404371,17z/data=!3m1!4b1!4m6!3m5!1s0x60013996bd8c6061:0xf96cacf357447456!8m2!3d34.685047!4d135.843012!16s%2Fm%2F02pwmjl?entry=ttu",
            Coords(lon=135.843012, lat=34.685047),
        ),
        (
            "https://www.google.com/maps/place/Nara+Park/@34.6850514,135.8404371,17z/data=!3m1!4b1!4m6!3m5!1s0x60013996bd8c6061:0xf96cacf357447456!8m2!3d34.685047!4d135.843012!16s%2Fm%2F02pwmjl?entry=ttu",
            Coords(lon=135.843012, lat=34.685047),
        ),
        (
            "https://www.google.com/maps/place/Osaka+Aquarium+Kaiyukan/@34.6545226,135.4263896,17z/data=!3m2!4b1!5s0x6000e8f48fa243ff:0x25fc1f29292f7889!4m6!3m5!1s0x6000e8f48c0da9cd:0x6f83c520ae082ccc!8m2!3d34.6545182!4d135.4289645!16zL20vMDJjeW13?entry=ttu",
            Coords(lon=135.4289645, lat=34.6545182),
        ),
        (
            "https://www.google.com/maps/place/Universal+Studios+Japan/@34.6656812,135.4297436,17z/data=!3m1!4b1!4m6!3m5!1s0x6000e0d083d5e25d:0x3605fe25303252aa!8m2!3d34.6656768!4d135.4323185!16zL20vMDczN3g1?entry=ttu",
            Coords(lon=135.4323185, lat=34.6656768),
        ),
        (
            "https://www.google.com/maps/place/Himeji+Castle/@34.8394534,134.6913298,17z/data=!3m1!4b1!4m6!3m5!1s0x3554e003a23324b3:0x7a4f8c2f6eba81b1!8m2!3d34.839449!4d134.6939047!16zL20vMDE4bmN4?entry=ttu",
            Coords(lon=134.6939047, lat=34.839449),
        ),
        (
            "https://www.google.com/maps/place/Fushimi+Inari+Taisha/@34.9676989,135.7766127,17z/data=!3m1!4b1!4m6!3m5!1s0x60010f153d2e6d21:0x7b1aca1c753ae2e9!8m2!3d34.9676945!4d135.7791876!16zL20vMDVsZHJt?entry=ttu",
            Coords(lon=135.7791876, lat=34.9676945),
        ),
        (
            "https://www.google.com/maps/place/Isonokami+Jingu/@34.5976917,135.849484,17z/data=!3m1!4b1!4m6!3m5!1s0x6001369c21dd83ab:0xb17ee3d081262f4c!8m2!3d34.5976873!4d135.8520589!16zL20vMDNkNG03?entry=ttu",
            Coords(lon=135.8520589, lat=34.5976873),
        ),
        (
            "https://www.google.com/maps/place/Omiwa+Jinja/@34.5287054,135.8457166,17z/data=!4m10!1m2!2m1!1sOmiwa+Jinja!3m6!1s0x601cfc17fc692b61:0xbb3334d79bfc028a!8m2!3d34.5287943!4d135.8532348!15sCgtPbWl3YSBKaW5qYVoNIgtvbWl3YSBqaW5qYZIBDXNoaW50b19zaHJpbmXgAQA!16s%2Fm%2F064n67z?entry=ttu",
            Coords(lon=135.8532348, lat=34.5287943),
        ),
        (
            "https://www.google.com/maps/place/Arashiyama+Bamboo+Forest/@35.0168231,135.6687264,17z/data=!3m1!4b1!4m6!3m5!1s0x6001abebbf5c8bad:0xfb9ffc7bbdd67cdd!8m2!3d35.0168187!4d135.6713013!16s%2Fg%2F11bx1hnfm7?entry=ttu",
            Coords(lon=135.6713013, lat=35.0168187),
        ),
        (
            "https://www.google.com/maps/place/Mount+Takao/@35.6254291,139.2334388,15z/data=!3m1!4b1!4m6!3m5!1s0x6019197f5ea3876f:0xc7070b841ef62fdf!8m2!3d35.6254126!4d139.2437385!16zL20vMDVzNWcx?entry=ttu",
            Coords(lon=139.2437385, lat=35.6254126),
        ),
        (
            "https://www.google.com/maps/place/Tateyama+Kurobe+Alpine+Route/@36.5832256,137.442958,17z/data=!3m1!4b1!4m6!3m5!1s0x5ff7e8b6792d22c3:0x5f89a4c762ddb1eb!8m2!3d36.5832213!4d137.4455329!16s%2Fg%2F11cmsz8wvs?entry=ttu",
            Coords(lon=137.4455329, lat=36.5832213),
        ),
        (
            "https://www.google.com/maps/place/Kenroku-en/@36.5621321,136.6600766,17z/data=!3m1!4b1!4m6!3m5!1s0x5ff83383f9b25905:0x970a7b3df003f2e4!8m2!3d36.5621278!4d136.6626515!16zL20vMDJsNnZ4?entry=ttu",
            Coords(lon=136.6626515, lat=36.5621278),
        ),
        (
            "https://www.google.com/maps/place/Mount+Shirouma/@36.7587343,137.7482898,15z/data=!3m1!4b1!4m6!3m5!1s0x5ff7cbce8a41e5db:0x410894def7f0130!8m2!3d36.7587181!4d137.7585895!16s%2Fm%2F080fx2b?entry=ttu",
            Coords(lon=137.7585895, lat=36.7587181),
        ),
        (
            "https://www.google.com/maps/place/Omicho+Market/@36.5717378,136.6532902,17z/data=!3m2!4b1!5s0x5ff8337052590bcf:0x4255ed9b2fe39923!4m6!3m5!1s0x5ff83370f7d313d3:0xbff4287c6ca534a5!8m2!3d36.5717335!4d136.6558651!16s%2Fg%2F1222j5wy?entry=ttu",
            Coords(lon=136.6558651, lat=36.5717335),
        ),
        (
            "https://www.google.com/maps/place/Higashi+Chaya+District/@36.5724921,136.6669815,17z/data=!3m1!4b1!4m6!3m5!1s0x5ff83374a1baf0b1:0xbb8c7a215e6a0d74!8m2!3d36.5724921!4d136.6669815!16s%2Fg%2F1z449xs7l?entry=ttu",
            Coords(lon=136.6669815, lat=36.5724921),
        ),
        (
            "https://www.google.com/maps/place/Saiko+Iyashi-no-Sato+Nenba+(Traditional+Japanese+Village)/@35.5050066,138.4966823,11z/data=!4m6!3m5!1s0x601be1142cbd0f3f:0xe38f690fd5eaebe7!8m2!3d35.5050023!4d138.6614772!16s%2Fg%2F1224bt0l?entry=ttu",
            Coords(lon=138.6614772, lat=35.5050023),
        ),
        (
            "https://www.google.com/maps/place/Kubota+Itchiku+Art+Museum/@35.5273283,138.7572575,17z/data=!3m1!4b1!4m6!3m5!1s0x60195e54ac1214a9:0xa7d57c3639eb60dc!8m2!3d35.527324!4d138.7598324!16s%2Fg%2F1tg8jsnh?entry=ttu",
            Coords(lon=138.7598324, lat=35.527324),
        ),
    ],
)
def test_coords_from_url(url, coords):
    assert get_coords_from_url(url) == coords


@pytest.mark.parametrize(
    (
        "url",
        "coords_list",
    ),
    [
        (
            "https://www.google.com/maps/dir/Magome,+Nakatsugawa,+Gifu,+Japan/Tsumago-juku,+Azuma,+Nagiso,+Kiso+District,+Nagano+399-5302,+Japan/@35.5541856,137.5632207,14z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x601cb71add823007:0x7d766e65361116fa!2m2!1d137.5717516!2d35.5315174!1m5!1m1!1s0x601cb7e4a598bb33:0x87bc2c35315036f6!2m2!1d137.5956667!2d35.5775876!3e2?entry=ttu",
            [
                Coords(lon=137.5717516, lat=35.5315174),
                Coords(lon=137.5956667, lat=35.5775876),
            ],
        ),
        (
            "https://www.google.com/maps/dir/Magome,+Nakatsugawa,+Gifu,+Japan/Tsumago-juku,+Azuma,+Nagiso,+Kiso+District,+Nagano+399-5302,+Japan/Tadachi+%E7%94%B0%E7%AB%8B/@35.5541856,137.5632207,14z/data=!4m20!4m19!1m5!1m1!1s0x601cb71add823007:0x7d766e65361116fa!2m2!1d137.5717516!2d35.5315174!1m5!1m1!1s0x601cb7e4a598bb33:0x87bc2c35315036f6!2m2!1d137.5956667!2d35.5775876!1m5!1m1!1s0x601cc9bd3ccb26ed:0x1b1560620d4ac8d0!2m2!1d137.5489597!2d35.5882476!3e2?entry=ttu",
            [
                Coords(lon=137.5717516, lat=35.5315174),
                Coords(lon=137.5956667, lat=35.5775876),
                Coords(lon=137.5489597, lat=35.5882476),
            ],
        ),
    ],
)
def test_parse_directions_url(url, coords_list):
    assert parse_directions_url(url) == coords_list
