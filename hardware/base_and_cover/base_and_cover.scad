// Define dimensions. All in mm

num_cams = 8;

edge_thickness = 4; // Thickness of the raised edge where the holes are
edge_width_from_hole = 7; // Width of the edge, material on each side of the hole
hole_diameter = 6; // bolt hole diameter
bolthead_d = 12; // bolt head countersink diameter
bolthead_h = 2; // bolt head height (for countersink depth)
radius_to_hole = 50; // Distance from center to the center of the mounting holes
downangle = 32; // Angle in degrees cameras face downward
cord_hole_length = 20;
cord_hole_width = 10;
cord_hole_offset = 20;

// Alignment indent in edge
// picam base width is 13.5
picam_base_width = 14.1375;
// picam base thickness is 11.5, optimum size is
// 12.1375, but we want to give a little space for
// bad drilling and it's better to index against
// the side
picam_base_thickness = 12.2;
indent_depth = 2;
offset_of_hole = 0; // If the mounting bolt hole isn't centered you can adjust it

// Don't touch
rotate_angle = 360/num_cams;

module picam(){
    translate([14.5,17,8.15]){
        rotate([0, 0, 90 ]){
            import("raspicam.stl", convexity=10);
        }
    }
}

module lenswcone() {
    translate([14.5,17,5.15]){
        rotate([0, 0, 90 ]){
            union(){
                // Lens
                translate([0,0,33]){
                    rotate([90,0,0])
                        {cylinder(r=22.8832/2, h=40);}
                    }

                // Cone of lens view

                translate([0,-22,33]){
                    rotate([90,0,0])
                        {cylinder(r1=0, r2=45.568/2*2, h=19.727*2);}
                    }

                }
            }
        }
}

module lens() {
    translate([14.5,17,5.15]){
        rotate([0, 0, 90 ]){
            union(){
                // Lens
                translate([0,0,33]){
                    rotate([90,0,0])
                        {cylinder(r=22.8832/2, h=36);}
                    }

                }
            }
        }
}

// Holy Cameras Batman
// Camera lens loop
module camera_lenses() {
    for (cam = [1 : num_cams]){
        rotate([0,0,cam * rotate_angle + (360/num_cams)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, rotate_angle ]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            //picam();
                            lens();
                        }
                    }
                }
            }
        }
    }
}

module picams() {
    for (cam = [1 : num_cams]){
        rotate([0,0,cam * rotate_angle + (360/num_cams)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, rotate_angle ]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            picam();
                            lens();
                        }
                    }
                }
            }
        }
    }
}


module camera_holeswcone() {
    for (cam = [1 : num_cams]){
        rotate([0,0,cam * rotate_angle + (360/num_cams)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, rotate_angle ]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            //picam();
                            lenswcone();
                        }
                    }
                }
            }
        }
    }
}

num_sides = 36;
rotate_angle_sides = 360/num_sides;


// Camera Base
module camera_base() {
    mirror([0,1,0]){
        difference(){
            minkowski(){
                hull(){
                    for (cam = [1 : num_cams]){

                        rotate([0,0,cam * rotate_angle + (360/num_cams)]){
                            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                                rotate([0, downangle, -rotate_angle]){

                                    translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                                        cube([picam_base_thickness, picam_base_width, indent_depth]);
                                    }

                                }
                            }
                        }
                    }
                }
                sphere(3, $fn=36);
            }
            // Camera mount holes loop
            camera_mount_holes();

        }
    }
}

module camera_mount_holes(){
    for (cam = [1 : num_cams]){

        rotate([0,0,cam * rotate_angle + (360/num_cams)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, -rotate_angle]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            cube([picam_base_thickness, picam_base_width, indent_depth + 10]);
                        }
                        translate([0, 0, -(bolthead_h * 2 + 10)]){
                            cylinder(r = hole_diameter / 2, h = edge_thickness * 3 + 10, $fn = 64);
                            cylinder(r = bolthead_d / 2 + 0.1, h = bolthead_h + 10, $fn = 64);

                        }
                    }
                }
            }
        }
    }
}

module cord_holes(){
    for (cam = [1 : num_cams]){
        if(cam%2==0) {
            rotate([0,0,cam * rotate_angle + (360/num_cams) * 1.5]){
                translate([cord_hole_offset, 0, -20]){
                        minkowski(){
                            cube([cord_hole_length,cord_hole_width,100]);
                            sphere(1, $fn=16);
                        }
                }
            }
        }
    }
}



module central_post() {

    minkowski(){
        union(){
            cylinder(r1=15, r2=15, h=25, $fn=6);
            cylinder(r1=10, r2=10, h=80, $fn=36);
        }
        sphere(0.5, $fn=16);
    }
    cylinder(r=5, h=90, $fn=36);
}


module camera_hull() {
    hull(){
        camera_lenses();
        camera_base();

        translate([0,0,90]){
            rotate([0,180,45]){
                //mirror([0,1,0]){
                    //union(){
                    camera_base();
                    camera_lenses();
                    //picams();
                    //camera_base();
                    //}
                //}
            }
        }
    }
}

module cover() {
    difference(){
        translate([0,0,90]){
            rotate([0,180,45]){
                difference() {
                    minkowski() {
                        camera_hull();
                        sphere(2, $fn=36);
                    }
                    camera_hull();
                    cube([1000,1000,90],center=true);
                    translate([0,0,90]){
                        rotate([0,180,45]){
                            mirror([0,1,0]){
                                camera_base();
                                mirror([0,1,0]){camera_holeswcone();}
                                //camera_base();
                                //}
                            }
                        }
                    }
                    mirror([0,1,0]){
                        camera_holeswcone();
                    }
                }
            }
        }
        mirror([0,1,0]){camera_mount_holes();}
    }
}


module camera_base_top() {
    mirror([0,1,0]){
        cover();
    }
    rotate([0,180,0]){
        translate([0,0,-90]){
            translate([0,0,90]){
                rotate([0,180,45]){
                    difference() {
                        mirror([0,1,0]){
                            //union(){
                            camera_base();
                            //camera_lenses();
                            //camera_base();
                            //}
                        }
                        translate([0,0,90-2]){
                            rotate([0,180,0]){
                                central_post();
                            }
                        }
                    }
                }
            }
        }
    }
}

module nut_hole(){
    minkowski(){
        translate([0,0,-9]){
            cylinder(r=25.4/2, h=25.4*3/4, $fn=6);
        }
        sphere(1, $fn=16);
    }
}

module camera_base_bottom() {
    difference() {
        union(){
            central_post();
            camera_base();
            cover();
        }
        cord_holes();
        nut_hole();
    }
}

camera_base_top();
