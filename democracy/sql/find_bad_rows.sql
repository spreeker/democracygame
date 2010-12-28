
SELECT votes.object_id, COUNT(votes.object_id), votes.user_id FROM votes where is_archived=FALSE GROUP BY votes.object_id, votes.user_id
having COUNT(votes.object_id) > 1