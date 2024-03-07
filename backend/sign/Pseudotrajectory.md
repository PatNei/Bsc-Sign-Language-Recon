# Implementing Trajectories

## what is a trajectory?

The sequence of direction for each dimension between frames.
So, the first element consists of 3 values, the direction of movement between frame 1 and frame 2.

## What is a "3darray"?


list of pictures, that have been reduced to landmarks
list\[list\[landmarks\]\], where each landmark has 3 float coordinates (x,y,z).

## How to?

```
function MakeTrajectory(3darray) returns trajectory

    previous = 3darray.first
    trajectory = []

    for each seq in 3darray.rest do
        current = 3darray.first

        mean_cur = MEAN(current)
        mean_prev = MEAN(previous)

        next_elm_of_trajectory = []
        for each dimension in dimensions do
            mean_p = mean_prev[dimension]
            mean_c = mean_cur[dimension]

            if IsWithinBoundaries(mean_c, mean_p) then
                next_elm_of_trajectory.append(STATIONARY)
            else 
                if mean_c > mean_p then
                    next_elm_of_trajectory.append(UP)
                else if mean_c < mean_p
                    next_elm_of_trajectory.append(DOWN)
        previous <- current

    return trajectory
```
