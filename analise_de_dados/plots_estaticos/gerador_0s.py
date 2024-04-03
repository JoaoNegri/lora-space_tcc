import csv
import datetime

def generate_pattern_csv(start_time, end_time, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp', 'X', 'Y', 'Z'])
        current_time = start_time
        while current_time <= end_time:
            csv_writer.writerow([current_time.strftime('%d %b %Y %H:%M:%S.%f')[:-3], '0', '0', '0'])
            current_time += datetime.timedelta(seconds=1)

start_time = datetime.datetime(2020, 1, 1, 20, 0, 0)
end_time = datetime.datetime(2020, 1, 1, 20, 20, 0)
output_file = 'pattern.csv'

generate_pattern_csv(start_time, end_time, output_file)
