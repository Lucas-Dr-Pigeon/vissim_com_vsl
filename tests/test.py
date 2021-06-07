'''
do some testing in this file
'''
import vissim_v5.vissim_v5 as vissim




def test_create_networks():
    links = vissim.Links("./networks/example/test1.inp")

    coords = {'points3D': [(0,0), (10,15)]}
    links.create((0,0),(10,15))
    links.export("./networks/example/test2.inp")
    return 0



if __name__ == "__main__":
    test_create_networks()